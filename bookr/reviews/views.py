from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone

from reviews.forms import SearchForm
from reviews.utils import average_rating

from .models import Book, Contributor, Publisher, Review
from .forms import PublisherForm, ReviewForm

def index(request):
    return render(request, "base.html")

def review_edit(request: HttpRequest, book_pk: int, review_pk: int=None):
    book = get_object_or_404(Book, pk=book_pk)
    if review_pk:
        book_review = get_object_or_404(Review, pk=review_pk, book_id=book_pk)
    else:
        book_review = None

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=book_review)
        if form.is_valid():
            review_form = form.save(commit=False)
            review_form.book = book
            if book_review:
                review_form.date_edited = timezone.now()
                messages.success(request, f"Review for \"{book.title}\" updated.")
            else:
                messages.success(request, f"Review for \"{book.title}\" created.")
            review_form.save()
            form.save_m2m()
            return redirect("book_detail", book.pk)
    else:
        form = ReviewForm(instance=book_review)
    return render(request, "reviews/instance-form.html", 
        {
            "form": form, 
            "instance": book_review, 
            "model_type": "Review", 
            "related_model_type": "Book", 
            "related_instance": book})


def publisher_edit(request: HttpRequest, pk: int=None):
    if pk is not None:
        publisher = get_object_or_404(Publisher, pk=pk)
    else:
        publisher = None

    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            updated_publisher = form.save()
            if publisher is None:
                messages.success(request, f"Publisher \"{updated_publisher}\" was created.")
            else:
                messages.success(request, f"Publisher \"{updated_publisher}\" was updated.")
            return redirect("publisher_edit", updated_publisher.pk)
    else:
        form = PublisherForm(instance=publisher)
    return render(request, "reviews/instance-form.html", {"instance": publisher, "model_type": "Publisher", "form": form})

def book_search(request: HttpRequest):
    search_text = request.GET.get("search", "")
    search_form = SearchForm(request.GET)
    books = set()
    if search_form.is_valid() and (search := search_form.cleaned_data["search"]):
        search_query = search_form.cleaned_data.get('search_in', 'title')
        if search_query == 'title':
            books = Book.objects.filter(title__icontains=search)
        else:
            contributors = Contributor.objects.filter(first_names__icontains=search)
            for contributor in contributors:
                for book in contributor.book_set.all():
                    books.add(book)
            contributors = Contributor.objects.filter(last_names__icontains=search)
            for contributor in contributors:
                for book in contributor.book_set.all():
                    books.add(book)
    context = {
        "search_text": search_text,
        "form": search_form,
        "books": books
    }
    # print(Book.objects.filter(title__icontains=search_query))
    return render(request, "reviews/search-results.html", context)

def book_list(request: HttpRequest) -> HttpResponse:
    books = Book.objects.all()
    # print(books)
    book_list = []
    for book in books:
        reviews = book.review_set.all()
        if reviews:
            book_rating = average_rating([review.rating for review in reviews])
            no_of_reviews = len(reviews)
        else:
            book_rating = None
            no_of_reviews = 0
        book_list.append({
            'book': book,
            'book_rating': book_rating,
            'number_of_reviews': no_of_reviews,
            })
        context = {
            'book_list': book_list,
        }
    return render(request, 'reviews/books_list.html', context)

def book_detail(request: HttpRequest, id: int) -> HttpResponse:
    book = get_object_or_404(Book,pk=id)
    reviews = book.review_set.all()
    context = {"book": book, "reviews": reviews}
    if reviews:
        context["book_rating"] = average_rating([review.rating for review in reviews])
    else:
        context['book_rating'] = None
    return render(request, 'reviews/book_detail.html', context)