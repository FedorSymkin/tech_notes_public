from django.http import HttpResponse
from django.urls import reverse


def home(request):
    # Здесь криво, но это вспомогательная менюшка, для примера не принципиально
    return HttpResponse('''
        You are: {username} <br />
        <a href='{login}'>login</a> <br/>
        <a href='{logout}'>logout</a> <br/>
        <a href='{api_register}'>api_register</a> <br/>
        <a href='{api_get_token}'>api_get_token</a> <br/>
        <a href='{api_posts_list}'>api_posts_list</a> <br/>
        <a href='{api_post_new}'>api_post_new</a> <br/>
    '''.format(
        username=request.user.username or 'anonymous',
        login=reverse('login'),
        logout=reverse('logout'),
        api_register=reverse('register', current_app='myapp'),
        api_get_token=reverse('get_token', current_app='myapp'),
        api_posts_list=reverse('posts_list', current_app='myapp'),
        api_post_new=reverse('post_new', current_app='myapp'),
    ))
