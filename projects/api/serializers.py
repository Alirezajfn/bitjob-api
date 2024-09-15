from rest_framework import serializers
from projects.models import Project, Category, Tag, ProjectFile


class CategoryProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'slug']


class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['file', 'uploaded_at']


class ProjectSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        read_only=False
    )

    tags = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Tag.objects.all(),
        many=True,
        read_only=False
    )

    files = ProjectFileSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'title', 'description', 'category', 'tags', 'owner',
            'budget', 'deadline', 'status', 'files',
            'created_at', 'updated_at', 'slug'
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        project = Project.objects.create(**validated_data)
        project.tags.set(tags)
        project.save()

        return project

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.set(tags)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.budget = validated_data.get('budget', instance.budget)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.status = validated_data.get('status', instance.status)

        instance.save()
        return instance
