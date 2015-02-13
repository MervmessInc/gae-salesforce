"""This file is loaded when starting a new application instance."""
import vendor

# add `lib' as a site packages directory, so our `main` module can load
# third-party libraries.
vendor.add('lib')