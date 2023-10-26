from django.http import HttpResponse

from recipes.models import ShoppingList


def collect_shopping_cart(request):
    """ Создание списка покупок.
    Позволяет пользователям получать список покупок в виде TXT файла,
    где все ингредиенты будут суммированы.
    """
    shopping_cart = ShoppingList.objects.filter(user=request.user).all()
    shopping_list = {}
    for item in shopping_cart:
        for recipe_ingredient in item.recipe.recipe_ingredients.all():
            name = recipe_ingredient.ingredient.name
            measuring_unit = recipe_ingredient.ingredient.measurement_unit
            amount = recipe_ingredient.amount
            if name not in shopping_list:
                shopping_list[name] = {
                    'name': name,
                    'measurement_unit': measuring_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
    content = (
        [f'{item["name"]} ({item["measurement_unit"]}) '
         f'- {item["amount"]}\n'
         for item in shopping_list.values()]
    )
    filename = 'shopping_list.txt'
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = (
        f'attachment; filename={0}'.format(filename)
    )
    return response
