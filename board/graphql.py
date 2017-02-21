from django.contrib.auth import get_user_model
from graphene import ObjectType, Node, Schema
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from board import models


class User(DjangoObjectType):
    class Meta:
        model = get_user_model()
        interfaces = (Node,)


class VerifType(DjangoObjectType):
    class Meta:
        model = models.VerifType
        interfaces = (Node,)
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }


class Verif(DjangoObjectType):
    class Meta:
        model = models.Verif
        interfaces = (Node,)
        filter_fields = {
            'tag': ['exact', 'icontains', 'istartswith'],
            'display_name': ['exact', 'icontains', 'istartswith'],
            'mandatory': ['exact'],
            'type__name': ['exact'],
        }


class VerifValue(DjangoObjectType):
    class Meta:
        model = models.VerifValue
        interfaces = (Node,)
        filter_fields = {
            'value': ['exact', 'icontains', 'istartswith'],
            'verif': ['exact'],
        }


class Query(ObjectType):
    verif_type = Node.Field(VerifType)
    all_verif_types = DjangoFilterConnectionField(VerifType)

    verif = Node.Field(Verif)
    all_verifs = DjangoFilterConnectionField(Verif)

    verif_value = Node.Field(VerifValue)
    all_verif_values = DjangoFilterConnectionField(VerifValue)


schema = Schema(query=Query,
                types=[Verif, VerifType, VerifValue])
