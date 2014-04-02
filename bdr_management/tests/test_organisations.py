import factory


class OrganisationFactory(factory.django.DjangoModelFactory):

    FACTORY_FOR = 'bdr_registry.Organisation'
    FACTORY_DJANGO_GET_OR_CREATE = (
        'name',
    )

    name = 'FIBRAN BULGARIA S.A.'

