from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password

from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .models import User, Post, Comment, session

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = make_password(serializer.validated_data['password'])

            new_user = User(username=username, email=email, password_hash=password)
            session.add(new_user)
            session.commit()
            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = session.query(User).filter_by(username=username).first()
        if user and check_password(password, user.password_hash):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role not in ['admin', 'author']:
            return Response({'error': 'You do not have permission to create a post.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            new_post = Post(
                title=serializer.validated_data['title'],
                content=serializer.validated_data['content'],
                author_id=user.id
            )
            session.add(new_post)
            session.commit()
            return Response({'message': 'Post created successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostListView(APIView):
    def get(self, request):
        author_username = request.query_params.get('author')
        query = session.query(Post)
        if author_username:
            user = session.query(User).filter_by(username=author_username).first()
            if user:
                query = query.filter_by(author_id=user.id)
            else:
                return Response({'error': 'Author not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Pagination Logic
        page = int(request.query_params.get('page', 1))
        page_size = 2
        posts = query.offset((page - 1) * page_size).limit(page_size).all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        post = session.query(Post).filter_by(id=post_id).first()
        if not post:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            new_comment = Comment(
                content=serializer.validated_data['content'],
                post_id=post_id,
                user_id=user.id
            )
            session.add(new_comment)
            session.commit()
            return Response({'message': 'Comment added successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
