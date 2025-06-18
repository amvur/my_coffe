import logging

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import OrderTableSerializers, ProductsSerializers, OrderItemSerializers
from .forms import OrderForm, DateRangeForm, ProductForm, OrderFilterForm
from .models import *
import datetime

from .tests import order

logger = logging.getLogger(__name__)


@receiver(connection_created)
def set_time_zone(sender, connection, **kwargs):
    if connection.vendor == 'pasgst':
        cursor = connection.cursor()
        cursor.execute("PRAGMA timezone = 'Europe/Moscow';")

class CreateProductAPIVew(APIView):
    def post(self, request):
        serialize = ProductsSerializers(data=request.data)
        if not serialize.is_valid():
            logger.error(f'Ошибка формы {serialize.errors}')
            return Response({
                'error':  "Invalid data", "details": serialize.errors
            },
                status = status.HTTP_400_BAD_REQUEST
            )
        try:
            product = serialize.save()



            return Response(
                {
                    'product':product
                },
                status= status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f'Ошибка создания заказа: {str(e)}', exc_info=True)
            return Response({
                "error": 'Product create failed'
            },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# def created_products_list(request):
#     if request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Продукт успешно создан")
#             return redirect("product_list")
#     else:
#         form = ProductForm()
#
#     return render(request, "directory/created_products_list.html", {"form": form})
#
#

def product_list(request):
    """Отображение списка товаров."""
    products = Products.objects.all()
    return render(request, 'directory/product_list.html', {'products': products})


class CreateOrderAPIew(APIView):
    def get(self, request):
        categories = (
            Products.objects
            .exclude(categpry__isnull=True)
            .order_by("category__name")
            .velues_list('category__name', float=True)
            .distinct()
        )
        products_by_category = {}
        for category in categories:
            products = Products.objects.filter(
                category__name=category  # Добавляем фильтр по активности
            ).order_by('name')
            if products.exists():  # Добавляем только непустые категории
                products_by_category[category] = products
        return Response({
            "products_by_category": products_by_category
        })

    def post(self, request):
        serialize = OrderTableSerializers(data=request.data)
        if not serialize.is_valid():
            logger.error(f'Ошибка формы : {serialize.errors}')
            return Response({"Error": "Invalid data", "details": serialize.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                oder = serialize.save(date=timezone.now(), status='unpaid')
                items_added = 0
                for product in Products.objects.all():
                    count = request.data.get(f"product_{product.id}", 0)
                    try:
                        count = int(count)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            count=count,
                            price=product.price
                        )
                        items_added += 1
                    except ValueError:
                        logger.warning(f"Некорректное количество для товара {product.id}")
                        continue
                    if items_added == 0:
                        order.delete()
                        return Response(
                            {"error": 'No items added'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    return Response({
                        "success": True,
                        "order_id": order.id, },
                        status=status.HTTP_201_CREATED
                    )
        except Exception as e:
            logger.error(f'Ошибка создания заказа: {str(e)}', exc_info=True)
            return Response({
                "error": 'Order create failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def create_order(request):
#     categories = (
#         Products.objects
#         .exclude(category__isnull=True)
#         .order_by('category__name')
#         .values_list('category__name', flat=True)
#         .distinct()
#     )
#
#     # Формируем словарь с активными товарами
#     products_by_category = {}
#     for category in categories:
#         products = Products.objects.filter(
#             category__name=category  # Добавляем фильтр по активности
#         ).order_by('name')
#         if products.exists():  # Добавляем только непустые категории
#             products_by_category[category] = products
#
#     if request.method == 'POST':
#         order_form = OrderForm(request.POST)
#         if order_form.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Создаем заказ
#                     order = order_form.save(commit=False)
#                     order.date = timezone.now()
#                     order.status = 'unpaid'  # Статус устанавливается явно
#                     order.save()
#
#                     # Обрабатываем товары в заказе
#                     items_added = 0
#                     for product in Products.objects.all():
#                         count_str = request.POST.get(f'product_{product.id}', '0')
#                         try:
#                             count = int(count_str)
#                             if count > 0:
#                                 OrderItem.objects.create(
#                                     order=order,
#                                     product=product,
#                                     count=count,
#                                     price=product.price,
#                                     sum=count * product.price
#                                 )
#                                 items_added += 1
#                                 logger.debug(f"Добавлен товар {product.id}, количество: {count}")
#
#                         except ValueError:
#                             logger.warning(f"Некорректное количество для товара {product.id}: {count_str}")
#                             continue
#
#                     if items_added == 0:
#                         order.delete()
#                         messages.warning(request, "Заказ не создан: не выбрано ни одного товара")
#                         return redirect('order_list')
#
#                     messages.success(request, f"Заказ #{order.id} успешно создан")
#                     return redirect('order_list')
#
#             except Exception as e:
#                 logger.error(f"Ошибка создания заказа: {str(e)}", exc_info=True)
#                 # return JsonResponse("Произошла ошибка при создании заказа. Пожалуйста, попробуйте еще раз.", status=400)
#                 messages.error(request, "Произошла ошибка при создании заказа. Пожалуйста, попробуйте еще раз.")
#         else:
#             logger.error(f"Ошибки формы: {order_form.errors}")
#             # return JsonResponse("Пожалуйста, исправьте ошибки в форме.", status=400)
#             messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
#     else:
#         order_form = OrderForm()
#     return JsonResponse(status=HTTP_200_OK)
#     return render(request, 'directory/create_order.html', {
#         'order_form': order_form,
#         'products_by_category': products_by_category,
#         'mode': 'create'
#     })


class EditOrderAPIVew(APIView):
    def get(self, request, order_id):
        order = get_object_or_404(OrderTable, id=order_id)
        order_items = order.orderitem_set.all()

        categories = (
            Products.objects
            .exclude(catergory__inull=True)
            .order_by("category__name")
            .values_list('category_name', flat=True)
            .distinct()
        )
        products_by_category = {}
        for category in categories:
            products = Products.objects.filetr(
                category__name=category
            ).order_by('name')
            if products.exists():
                products_by_category[category] = products
        return Response({
            'order': OrderTableSerializers(order).data,
            'order_items': OrderItemSerializers(order_items, many=True).data,
            'products_by_category': products_by_category,
        })

    def put(self, request, order_id):
        order = get_object_or_404(OrderTable, id=order_id)
        serializer = OrderTableSerializers(order, data=request.data, partial=True)

        if not serializer.is_valid():
            logger.error(f'Order form Errs=or {serializer.errors}')
            return Response({'error': "invalid data", 'details': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Обновляем данные заказа
                order = serializer.save()
                # Удаляем старый
                order.orderitem_set.all().delete()
                item_added = 0

                for product in Products.objects.all():
                    product_key = f"product_{product.id}"
                    if product_key in request.data:
                        count = request.data[product_key]
                        try:
                            # count = int(count)
                            if int(count) > 0:
                                OrderItem.objects.create(
                                    order=order,
                                    product=product,
                                    count=count,
                                    price=product.price,
                                    sum=product.price * count
                                )
                                item_added += 1
                        except ValueError:
                            logger.error(f'Invalid quantity for product {product.id}')
                            continue
                        if item_added == 0:
                            return Response({
                                "error": "No items added"
                            },
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        return Response({
                            'success': True,
                            'order_id': order_id,
                            'status': order.status
                        },
                            status=status.HTTP_200_OK
                        )
        except Exception as e:
            logger.error(f"Order update error: {str(e)}", exc_info=True)
            return Response({
                "error": "Order update failed"
            },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# def edit_order(request, order_id):
#     order = get_object_or_404(OrderTable, id=order_id)
#     order_items = order.orderitem_set.all()
#
#     # Получаем все категории (без фильтрации по is_active)
#     categories = (
#         Products.objects
#         .exclude(category__isnull=True)
#         .order_by('category__name')
#         .values_list('category__name', flat=True)
#         .distinct()
#     )
#
#     # Формируем словарь с товарами по категориям
#     products_by_category = {}
#     for category in categories:
#         products = Products.objects.filter(
#             category__name=category
#         ).order_by('name')
#         if products.exists():
#             products_by_category[category] = products
#
#     if request.method == 'POST':
#         order_form = OrderForm(request.POST, instance=order)
#         if order_form.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Сохраняем изменения в заказе
#                     order = order_form.save(commit=False)
#                     order.save()
#
#                     # Удаляем все текущие товары в заказе
#                     order.orderitem_set.all().delete()
#
#                     # Обрабатываем новые товары из формы
#                     items_added = 0
#                     for key, value in request.POST.items():
#                         if key.startswith('product_'):
#                             product_id = key.split('_')[1]
#                             try:
#                                 product = Products.objects.get(id=product_id)
#                                 count = int(value)
#                                 if count > 0:
#                                     OrderItem.objects.create(
#                                         order=order,
#                                         product=product,
#                                         count=count,
#                                         price=product.price,
#                                         sum=count * product.price
#                                     )
#                                     items_added += 1
#                             except (ValueError, Products.DoesNotExist):
#                                 continue
#
#                     if items_added == 0:
#                         messages.warning(request, "В заказе нет товаров")
#                     else:
#                         messages.success(request, f"Заказ #{order.id} успешно обновлен")
#
#                     return redirect('order_list')
#
#             except Exception as e:
#                 logger.error(f"Ошибка обновления заказа {order_id}: {str(e)}", exc_info=True)
#                 messages.error(request, f"Ошибка при обновлении заказа: {str(e)}")
#         else:
#             messages.error(request, "Пожалуйста, исправьте ошибки в форме")
#     else:
#         # Создаем словарь с текущими количествами товаров
#         initial_counts = {item.product.id: item.count for item in order_items}
#         order_form = OrderForm(instance=order)
#
#     return render(request, 'directory/edit_order.html', {
#         'order_form': order_form,
#         'products_by_category': products_by_category,
#         'initial_counts': initial_counts,
#         'order': order,
#         'mode': 'edit'
#     })


@permission_required('orders.view_order', raise_exception=True)
def order_list(request):
    today = timezone.now().date()

    # Инициализация форм с GET-параметрами
    filter_form = OrderFilterForm(request.GET or None)
    date_form = DateRangeForm(request.GET or None, initial={'start_date': today, 'end_date': today})

    # Обработка фильтров
    start_date = today
    end_date = today
    status_filter = None

    if filter_form.is_valid():
        status_filter = filter_form.cleaned_data.get('status')

    if date_form.is_valid():
        start_date = date_form.cleaned_data['start_date']
        end_date = date_form.cleaned_data['end_date']

    # Фильтрация заказов
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

    orders = OrderTable.objects.filter(
        date__gte=start_datetime,
        date__lte=end_datetime
    ).order_by('-date')

    if status_filter:
        orders = orders.filter(status=status_filter)

    # Аннотация и агрегация
    orders = orders.prefetch_related('orderitem_set').annotate(
        total_sum=Sum('orderitem__sum')
    )
    total_paid_sum = orders.filter(status='paid').aggregate(
        total=Sum('total_sum')
    )['total'] or 0

    # Обработка изменения статуса
    if request.method == 'POST' and 'order_id' in request.POST:
        if not request.user.has_perm('orders.change_order'):
            return HttpResponseForbidden("У вас нет прав на изменение заказов")

        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        if new_status in dict(OrderTable.STATUS_CHOICES).keys():
            order = get_object_or_404(OrderTable, id=order_id)
            order.status = new_status
            order.save()

            # Сохраняем параметры фильтрации для редиректа
            params = request.GET.urlencode()
            redirect_url = f"{reverse('order_list')}?{params}" if params else reverse('order_list')
            return redirect(redirect_url)

    # Пагинация
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'date_form': date_form,
        'total_order_sum': total_paid_sum,
        'status_choices': OrderTable.STATUS_CHOICES,
    }
    return render(request, 'directory/order_list.html', context)


def mark_order_as_paid(request, order_id):
    try:
        order = get_object_or_404(OrderTable, id=order_id)
        if order.status != 'cash' or order.status != 'without_cash':
            with transaction.atomic():
                order.status = 'cash'
                order.save()
                logger.info(f"Заказ {order_id} оплачен")
                messages.success(request, "Заказ оплачен")
        else:
            messages.warning(request, "Заказ уже оплачен")
    except Exception as e:
        logger.error(f"Ошибка оплаты заказа {order_id}: {str(e)}")
        messages.error(request, "Ошибка оплаты")
    return redirect('order_list')


@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(OrderTable, id=order_id)
    order.status = 'canceled'
    order.save()
    messages.success(request, f'Заказ #{order.id} отменен')
    return redirect('edit_order', order_id=order.id)


def cancel_order(request, order_id):
    order = get_object_or_404(OrderTable, id=order_id)
    if order.status == 'paid':
        order.status = 'canceled'
        order.save()
        messages.success(request, "Заказ отменен. ПКО удален.")
    elif order.status == 'unpaid':
        order.status = 'canceled'
        order.save()
        messages.success(request, "Неоплаченный заказ отменен.")
    else:
        messages.warning(request, "Заказ уже отменен.")
    return redirect('order_list')


@ensure_csrf_cookie
@require_POST
def update_order_status(request, order_id):
    if not request.user.has_perm('orders.change_order'):
        return HttpResponseForbidden("У вас нет прав на изменение заказов")

    order = get_object_or_404(OrderTable, id=order_id)
    new_status = request.POST.get('status')

    if new_status not in dict(OrderTable.STATUS_CHOICES).keys():
        return JsonResponse({'error': 'Недопустимый статус'}, status=400)

    order.status = new_status
    order.save()

    return redirect('order_list')


def cashreceiptorderviews(request):
    # Собираем все объекты обоих типов в один список
    cash_orders = CashReceiptOrder.objects.all().order_by('-date')
    payment_orders = PaymentOrder.objects.all().order_by('-date')

    # Объединяем querysets
    combined_orders = sorted(
        list(cash_orders) + list(payment_orders),
        key=lambda x: x.date,
        reverse=True
    )

    # Получаем текущую дату
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)

    # Пагинация
    paginator = Paginator(combined_orders, 10)  # 10 элементов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Общие суммы
    total_cash = cash_orders.aggregate(total=Sum('sum'))['total'] or 0
    total_payment = payment_orders.aggregate(total=Sum('sum'))['total'] or 0
    total_sum = total_cash + total_payment

    # Сумма за текущий день
    daily_cash = CashReceiptOrder.objects.filter(
        date__year=today.year,
        date__month=today.month,
        date__day=today.day
    ).aggregate(total=Sum('sum'))['total'] or 0

    daily_payment = PaymentOrder.objects.filter(
        date__year=today.year,
        date__month=today.month,
        date__day=today.day
    ).aggregate(total=Sum('sum'))['total'] or 0
    daily_sum = daily_cash + daily_payment

    # Сумма за текущий месяц
    monthly_cash = CashReceiptOrder.objects.filter(
        date__year=first_day_of_month.year,
        date__month=first_day_of_month.month
    ).aggregate(total=Sum('sum'))['total'] or 0

    monthly_payment = PaymentOrder.objects.filter(
        date__year=first_day_of_month.year,
        date__month=first_day_of_month.month
    ).aggregate(total=Sum('sum'))['total'] or 0
    monthly_sum = monthly_cash + monthly_payment

    return render(request, 'directory/pko_list.html', {
        'page_obj': page_obj,
        'total_sum': total_sum,
        'daily_sum': daily_sum,
        'monthly_sum': monthly_sum,
        'current_date': today.strftime("%d.%m.%Y"),
        'current_month': first_day_of_month.strftime("%m.%Y")
    })
