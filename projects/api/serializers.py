from rest_framework import serializers
from projects.models import Project, Category, Tag, ProjectFile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['id', 'file', 'uploaded_at']


class ProjectSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category',
                                                     write_only=True)

    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, source='tags',
                                                 write_only=True)

    files = ProjectFileSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'category', 'category_id', 'tags', 'tag_ids',
            'owner', 'budget', 'deadline', 'status', 'files', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        category = validated_data.pop('category')
        tags = validated_data.pop('tags')

        project = Project.objects.create(**validated_data)

        project.category = category
        project.tags.set(tags)
        project.save()

        return project

    def update(self, instance, validated_data):
        category = validated_data.pop('category', None)
        tags = validated_data.pop('tags', None)

        if category:
            instance.category = category
        if tags:
            instance.tags.set(tags)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.budget = validated_data.get('budget', instance.budget)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.status = validated_data.get('status', instance.status)

        instance.save()
        return instance
