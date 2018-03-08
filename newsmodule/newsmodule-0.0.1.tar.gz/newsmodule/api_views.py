# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import datetime, calendar, requests
from . import models, serializers
from rest_framework import generics, status
from django.db.models import Q, Count
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


# post module
class TagListView(generics.ListCreateAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class CategoryListView(generics.ListCreateAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer


class PostListView(generics.ListCreateAPIView):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.PostDetailSerializer
        else:
            return serializers.PostSerializer

    def get(self, request):
        queryset = models.Post.objects.all()
        kwargs = request.query_params
        if kwargs.get('tag'):
            queryset = queryset.filter(tags__name=kwargs['tag'])
        if kwargs.get('pub_time_begin'):
            queryset = queryset.filter(pub_time__gte=kwargs['pub_time_begin'])
        if kwargs.get('pub_time_end'):
            queryset = queryset.filter(pub_time__lte=kwargs['pub_time_end'])
        if kwargs.get('category'):
            queryset = queryset.filter(categories__pk=int(kwargs['category']))
        if kwargs.get('org'):
            queryset = queryset.filter(publisher__account__org_code=kwargs['org'])
        if kwargs.get('title'):
            queryset = queryset.filter(title__contains=kwargs['title'])
        if kwargs.get('abstract'):
            queryset = queryset.filter(abstract__contains=kwargs['abstract'])
        if kwargs.get('raw'):
            queryset = queryset.filter(raw__contains=kwargs['raw'])
        if kwargs.get('search'):
            keyword = kwargs['search']
            queryset = queryset.filter(
                Q(title__contains=keyword)
                | Q(abstract__contains=keyword)
                | Q(raw__contains=keyword))
        if kwargs.get('publisher'):
            queryset = queryset.filter(publisher__pk=int(kwargs['publisher']))
        if kwargs.get('keyword'):
            keywords = kwargs.get('keyword').replace(' ', '').split(',')
            query = Q()
            for i, keyword in enumerate(keywords):
                query = query | Q(keyword__contains=keyword)
            queryset = queryset.filter(query)
        if kwargs.get('is_draft'):
            if kwargs['is_draft'] == 'true':
                queryset = queryset.filter(is_draft=True)
            else:
                queryset = queryset.filter(is_draft=False)
        queryset = queryset.distinct().order_by('-pub_time')

        if int(kwargs.get('page', 0)) > 0:
            page_size = int(kwargs.get('page_size', 10))
            page = int(kwargs.get('page', 1))
            data = Paginator(queryset, page_size)
            if page > data.num_pages:
                return Response('Invalid page', status=400)
            serializer = serializers.PostDetailSerializer(data.page(page), many=True)
            result = {
                "count": queryset.count(),
                "page_size": page_size,
                "page": page,
                "data": serializer.data,
                "total_pages": data.num_pages
            }
            return Response(result)

        else:
            serializer = serializers.PostDetailSerializer(queryset, many=True)
            return Response(serializer.data)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.PostDetailSerializer
        else:
            return serializers.PostSerializer

    def perform_update(self, serializer):
        instance = serializer.save()

        if not serializer.validated_data.get('update_time'):
            instance.update_time = datetime.datetime.now()
        instance.save()

class WebReadPostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user_read = models.UserWebReadPost.objects.filter(user=self.request.user)
        if not user_read:
            return Response(list())
        queryset = user_read[0].web_read_post.all()
        query = request.query_params
        if query.get('tag'):
            queryset = queryset.filter(tags__name=query['tag'])
        serializer = serializers.PostDetailSerializer(queryset, many=True)
        return Response(serializer.data)

class MobileReadPostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_read = models.UserMobileReadPost.objects.filter(user=self.request.user)
        if not user_read:
            return Response(list())
        queryset = user_read[0].mobile_read_post.all()
        query = request.query_params
        if query.get('tag'):
            queryset = queryset.filter(tags__name=query['tag'])
        serializer = serializers.PostDetailSerializer(queryset, many=True)
        return Response(serializer.data)

class UserReadPostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_read = models.UserReadPost.objects.filter(user=self.request.user)
        if not user_read:
            return Response(list())
        queryset = user_read[0].post_ids.all()
        query = request.query_params
        if query.get('tag'):
            queryset = queryset.filter(tags__name=query['tag'])
        serializer = serializers.PostDetailSerializer(queryset, many=True)
        return Response(serializer.data)


class UserUnReadPostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_read = models.UserReadPost.objects.filter(user=self.request.user)
        query = request.query_params
        if not user_read:
            queryset = models.Post.objects.all()
            if query.get('tag'):
                queryset = queryset.filter(tags_name=query['tag'])
            serializer = serializers.PostDetailSerializer(queryset, many=True)
            return Response(serializer.data)
        queryset = models.Post.objects.all().exclude(userreadpost=user_read[0])
        if query.get('tag'):
            queryset = queryset.filter(tags__name=query['tag'])
        serializer = serializers.PostDetailSerializer(queryset, many=True)
        return Response(serializer.data)
