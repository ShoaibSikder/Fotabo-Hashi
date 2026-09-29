import factory

from apps.accounts.models import User, UserRole


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda number: f"user{number}@example.com")
    role = UserRole.USER
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or "StrongPassword123!")
        if create:
            obj.save(update_fields=["password"])


class AdminUserFactory(UserFactory):
    role = UserRole.ADMIN
    is_staff = True
    is_superuser = True
