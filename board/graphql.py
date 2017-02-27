from graphene import ObjectType, Node, Schema, Field
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from board import models


class Computer(DjangoObjectType):
    class Meta:
        model = models.Computer
        interfaces = (Node,)
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith']
        }


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


class ExceptionRule(DjangoObjectType):
    class Meta:
        model = models.ExceptionRule
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
                types=[Verif, VerifType, VerifValue, Computer, ExceptionRule])
