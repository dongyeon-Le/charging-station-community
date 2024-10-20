from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #----------------------------------------------------basic---------------------------------------------------------------
    path('', views.Index_Page, name = '메인페이지'),
    
    path('signup/', views.Signup_Page, name = '회원가입 페이지'),
    path('signup/duplicate/id', views.check_id_duplicate, name='아이디 중복확인'),

    path('login/', views.Login_Page, name = '로그인 페이지'),
    path('signup_action/', views.Signup_Action, name = '회원가입 액션'),
    path('login_action/', views.Login_Action, name = '로그인 액션'),
    path('logout/', views.Logout, name = '로그아웃'),

   #--------------------------------------------------------------------------------------------------------------------------


    path('board/', views.Board_Page, name = '게시판'),

    path('post_writing/', views.Post_Writing_Page, name = '게시판 글쓰기'),

    path('post_writing_action/', views.Post_Writing_Action, name = '게시판 글쓰기 액션'),

    path('post_detail/<int:post_id>/', views.Post_Detail_Page, name = '게시판 글정보'),

    path('mypage/', views.Myaccount_Page, name = '내정보'),

    path('edit_info', views.Edit_Info, name = '정보 수정'),

    path('user_detail/<int:connected_user_id>/', views.User_Detail_Page, name = 'User_Detail_Page'),

    path('delete_post/<int:post_id>', views.Delete_Post, name = '게시판 글삭제'),

    path('Ev_cumminity_detail/<str:station_name>/', views.Ev_cumminity_detail, name='전기차 충전소 정보'),

    path('location/', views.location_page, name='location_page'),  # 위치 정보를 출력하는 페이지


    path('post/<int:post_id>/comment/', views.add_comment, name='댓글 추가'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='댓글 삭제'),
    path('delete_post/<int:post_id>/', views.delete_post, name='게시글 삭제'),
    path('change_post/<int:post_id>/', views.change_post, name='게시글 수정'),
    path('change_post_action/<int:post_id>/', views.change_post_action, name='게시글 수정 액션'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
