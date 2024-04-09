from django.urls import path, include, re_path
from home.views import ProductListCreateView, ProductRetrieveUpdateDestroyView, CustomerListCreateView, CustomerRetrieveUpdateDestroyView, BillingAPIView

urlpatterns = [
    # Include the URLs from the `home` app
    path("", include("home.urls")),

    # Define a URL pattern for the `ProductListCreateView` view
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),

    # Define a URL pattern for the `ProductRetrieveUpdateDestroyView` view
    re_path(r"^products/(?P<pk>\d+)/$", ProductRetrieveUpdateDestroyView.as_view(), name="product-detail"),

    # Define a URL pattern for the `CustomerListCreateView` view
    path("customers/", CustomerListCreateView.as_view(), name="customer-list-create"),

    # Define a URL pattern for the `CustomerRetrieveUpdateDestroyView` view
    re_path(r"^customers/(?P<pk>\d+)/$", CustomerRetrieveUpdateDestroyView.as_view(), name="customer-detail"),

    # Define a URL pattern for the `BillingAPIView` view
    path("billing/", BillingAPIView.as_view(), name="billing"),
]