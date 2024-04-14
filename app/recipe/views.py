""""Views for the recipee APIs"""
from drf_spectacular.utils import (  # type: ignore
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (viewsets,
                            status,
                            mixins)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import (
                        Recipe,
                        Tag,
                        Ingredient,
                        )
from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='tags',
                type=OpenApiTypes.STR,
                description='Comma separated list of IDs to filter',
            ),
            OpenApiParameter(
                name='ingredients',
                type=OpenApiTypes.STR,
                description='Comma separated list of IDs to filter',
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage Recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_inst(self, qs):
        """Convert a list of strings to Integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieves recipes for authenticated users"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_inst(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_inst(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class"""
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='assigned_only',
                type=OpenApiTypes.INT, enum=[0, 1],
                description='filter by items assigned to recipes.',
            )
        ]
    )
)
class BaseRecipeAtrrViewSet(mixins.ListModelMixin,
                            viewsets.GenericViewSet,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin):
    """Base viewset for Recipe Attribute"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Filter queryset to authnticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipes__isnull=False)
        return queryset.filter(
            user=self.request.user).order_by('-name').distinct()


class TagViewSet(BaseRecipeAtrrViewSet):
    """Manage tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAtrrViewSet):
    """Manage Ingredient in the database"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
