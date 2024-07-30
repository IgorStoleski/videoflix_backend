from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
        Generate a hash value using the user's primary key, timestamp, and activation status.
        This method combines the user's primary key, the timestamp at which the token is generated,
        and the user's activation status to create a unique hash. This hash is used to securely verify
        the integrity of the account activation link sent to the user.
        :param user: The user instance for which the token is being generated.
        :type user: User model instance
        :param timestamp: The time at which the token is generated, typically the current time.
        :type timestamp: int
        :return: A string that represents the hash value combining the user's primary key,
                 timestamp, and activation status.
        """
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
        
account_activation_token = AccountActivationTokenGenerator()