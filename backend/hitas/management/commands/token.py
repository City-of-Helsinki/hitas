from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Hitas token generation"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--username", required=True, help="Username")
        parser.add_argument("--key", help="Set key to a given value")

    def handle(self, *args, **options) -> None:
        username = options["username"]
        key = options["key"]

        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            print(f"Error: User not found with username '{username}'.")
            return

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user, key=key)
        if key:
            print(f"Token set for user '{user.username}'.")
        else:
            print(f"Token created for user '{user.username}': {token}")
