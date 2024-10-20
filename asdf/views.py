from django.shortcuts import render, redirect
from asdf.models import Users, Posts, Comment
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
import random, time
from django.http import JsonResponse
import pandas as pd
from django.shortcuts import render
import folium

#----------------------------------------------------basic-------------------------------------------------------------------------------------------------
#관리자 설정
admin = 1

#첫 화면 페이지
def Index_Page(request):
    csv_file_path = 'asdf/static/csv/병합된_충전소_데이터_UTF8.csv'
    
    # pandas를 사용하여 CSV 파일 읽기
    df = pd.read_csv(csv_file_path)
    
    # 충전소명, 주소, 이용가능시간, 위도, 경도 컬럼 추출
    charging_stations = df[['충전소명', '충전소주소']].drop_duplicates()
    charging_station_names = list(set(charging_stations['충전소명'].tolist()))
    charging_station_address = list(set(charging_stations['충전소주소'].tolist()))
    charging_station_time = df['이용가능시간'].tolist()
    charging_station_latitude = df['위도'].tolist()
    charging_station_longitude = df['경도'].tolist()
    charging_location = df[['위도', '경도','충전소주소','충전소명']]

    # 선택된 도시와 시군구
    selected_city = request.GET.get('city')
    selected_district = request.GET.get('district')

    # 시군구 데이터 정의
    districts = {
        "서울특별시": [
        "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", 
        "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", 
        "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", 
        "은평구", "종로구", "중구", "중랑구"],
        "경기도": ["가평군", "고양시", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시", "부천시", "성남시", "수원시", "시흥시", "안산시", "안성시", "안양시", "양주시", "양평군", "여주시", "연천군", "오산시", "용인시", "의왕시", "의정부시", "파주시", "평택시", "포천시", "하남시", "화성시"],
        "인천": ["강화군", "계양구", "남동구", "동구", "미추홀구", "부평구", "서구", "연수구", "옹진군", "중구"],
        "부산": ["강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구"],
        "대전": ["서구", "유성구", "대덕구", "동구","중구"],
        "대구": ["중구", "동구", "서구", "남구", "달서구", "달성군", "북구", "수성구"],
        "울산": ["남구", "북구", "중구", "울주군"],
        "세종": ["고운동", "나성동", "다정동", "대평동", "도담동", "보람동", "새롬동", "소담동", "아름동", "어진동", "연기면 세종리", "연동면 명학리", "전의면 서정리", "조치원읍 상리", "종촌동", "한솔동"],
        "광주": ["동구", "서구", "남구", "북구","광산구"],
        "강원도": ["강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "평창읍", "홍천군", "화천군", "횡성군"],
        "충청북도": ["괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청주시", "충주시"],
        "충청남도": ["계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천군", "아산시", "예산군", "천안시", "청양군", "태안군", "홍성군"],
        "경상북도": ["경산시", "경주시", "고령군", "구미시", "군위군", "김천시", "문경시", "봉화군", "북구", "상주시", "성주군", "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "칠곡군", "포항시"],
        "경상남도": ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시", "통영시", "하동군", "함안군", "합천군"],
        "전라북도": ["고창군", "군산시", "김제시", "남원시", "전주시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군", "장수군", "정읍시", "진안군"],
        "전라남도": ["강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군"],
        "제주": ["제주시", "서귀포시"]
    }

    # 선택된 도시와 시군구에 대한 주소 필터링
    filtered_stations = charging_stations[
        charging_stations['충전소주소'].str.startswith(selected_city) &
        charging_stations['충전소주소'].str.contains(selected_district if selected_district else "")
    ] if selected_city else charging_stations

    filtered_location = charging_location[
        charging_location['충전소주소'].str.startswith(selected_city) &
        charging_location['충전소주소'].str.contains(selected_district if selected_district else "")
    ] if selected_city else charging_location

    # 선택된 시군구에 대한 목록 가져오기
    district_list = districts.get(selected_city, [])

    # 지도 시각화
    if not filtered_location.empty:
        lat = filtered_location.iloc[0]['위도']  # 첫 번째 주소의 위도
        long = filtered_location.iloc[0]['경도']  # 첫 번째 주소의 경도
    else:
        lat, long = 0, 0  # 기본값 (주소가 없을 경우)

    m = folium.Map([lat, long], zoom_start=15, tiles='OpenStreetMap')
    
    for station in filtered_location.itertuples(index=False):
       latitude = station.위도  # 위도
       longitude = station.경도  # 경도
       name = station.충전소명


       folium.Marker([latitude, longitude], icon=folium.Icon(color='red',icon='star'), tooltip=name).add_to(m)
    return render(request, "basic/main.html",
                   {
                      'charging_station_names': charging_station_names,
                      'filtered_stations': filtered_stations,  # 필터링된 충전소 데이터 추가
                      'charging_station_time': charging_station_time,
                      'charging_station_latitude': charging_station_latitude,
                      'charging_station_longitude': charging_station_longitude,
                      'district_list': district_list,
                      'selected_city': selected_city,
                      'selected_district': selected_district,
                      'result':m._repr_html_()
                  })

#회원가입 페이지
def Signup_Page(request):
    return render(request, "basic/signup.html")

#로그인 페이지
def Login_Page(request):
    return render(request, "basic/login.html")


#회원가입 정보 저장
def Signup_Action(request):
    # 입력받은 값 정의
    var_user_id = request.POST.get('input_user_id')
    var_password = request.POST.get('input_password')
    var_name = request.POST.get('input_name')
    var_email = request.POST.get('input_email')
    var_phone = request.POST.get('input_phone_1')+request.POST.get('input_phone_2')+request.POST.get('input_phone_3')
    var_address = request.POST.get('input_Address')
    var_address_detail = request.POST.get('input_Address_detail')


    # 빈 필드가 없는지 검증
    if var_user_id and var_password and var_name and var_email:

        # 입력받은 아이디, 이메일이 db에 존재하는지 검증
        if Users.objects.filter(user_id = var_user_id).exists():
            return redirect('회원가입 페이지')
    
        if Users.objects.filter(email = var_email).exists():
            return redirect('회원가입 페이지')
        
        # db에 입력받은 유저 정보 저장
        Users.objects.create(
            user_id = var_user_id,
            password = var_password,
            name = var_name,
            email = var_email,
            address = var_address,
            address_detail = var_address_detail,
            phone = var_phone
        )
        
        return render(request, "basic/login.html")

    else:
        return redirect('회원가입 페이지')
    
#로그인
def Login_Action(request):
    # 입력받은 값 정의
    var_user_id = request.POST.get('input_user_id')
    var_password = request.POST.get('input_password')

    # 빈 필드가 없는지 검증
    if var_user_id and var_password:

        select_user = Users.objects.filter(user_id = var_user_id).first()

        if select_user:
      
            if select_user.password == var_password:
                # 사용자를 로그인한다
                login(request, select_user)

                return redirect('메인페이지')

            else:
                return redirect('로그인 페이지')
        
        else:
            return redirect('로그인 페이지')
        
# 아이디 중복확인
def check_id_duplicate(request):
    input_user_id = request.GET.get('input_user_id', '')
    exists = Users.objects.filter(user_id=input_user_id).exists()
    return JsonResponse({'exists': exists})

          
#로그아웃 페이지
def Logout(request):
    request.session.flush()

    return redirect('메인페이지')

from django.db.models import Q
from django.core.paginator import Paginator

@login_required
def Board_Page(request):
    # 선택된 도시와 구/군을 GET 요청에서 가져옵니다.
    selected_city = request.GET.get('city')
    selected_district = request.GET.get('district')

    # 검색어를 GET 요청에서 가져옵니다.
    search_query = request.GET.get('search', '')

    # 각 도시별로 구/군 목록을 딕셔너리로 정의
    districts = {
        "서울특별시": ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"],
        "경기도": ["가평군", "고양시", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시", "부천시", "성남시", "수원시", "시흥시", "안산시", "안성시", "안양시", "양주시", "양평군", "여주시", "연천군", "오산시", "용인시", "의왕시", "의정부시", "파주시", "평택시", "포천시", "하남시", "화성시"],
        "인천": ["강화군", "계양구", "남동구", "동구", "미추홀구", "부평구", "서구", "연수구", "옹진군", "중구"],
        "부산": ["강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구"],
        "대전": ["서구", "유성구", "대덕구", "동구", "중구"],
        "대구": ["중구", "동구", "서구", "남구", "달서구", "달성군", "북구", "수성구"],
        "울산": ["남구", "북구", "중구", "울주군"],
        "세종": ["고운동", "나성동", "다정동", "대평동", "도담동", "보람동", "새롬동", "소담동", "아름동", "어진동", "연기면", "연동면", "전의면", "조치원읍", "종촌동", "한솔동"],
        "광주": ["동구", "서구", "남구", "북구", "광산구"],
        "강원도": ["강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "평창읍", "홍천군", "화천군", "횡성군"],
        "충청북도": ["괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청주시", "충주시"],
        "충청남도": ["계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천군", "아산시", "예산군", "천안시", "청양군", "태안군", "홍성군"],
        "경상북도": ["경산시", "경주시", "고령군", "구미시", "군위군", "김천시", "문경시", "봉화군", "상주시", "성주군", "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡군", "포항시"],
        "경상남도": ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시", "통영시", "하동군", "함안군", "함양군", "합천군"],
        "전라북도": ["고창군", "군산시", "김제시", "남원시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군", "장수군", "전주시", "정읍시", "진안군"],
        "전라남도": ["강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군"],
        "제주": ["서귀포시", "제주시"]
    }

    # 선택된 도시의 구/군 리스트를 가져옵니다.
    district_list = districts.get(selected_city, [])

    # 필터링을 위한 초기 쿼리셋 설정
    posts_queryset = Posts.objects.all()

    # 도시 선택 필터링
    if selected_city:
        posts_queryset = posts_queryset.filter(location__icontains=selected_city)

    # 구/군 선택 필터링
    if selected_city and selected_district:
        posts_queryset = posts_queryset.filter(location_detail__icontains=selected_district)

     # 검색어 필터링 추가
    if search_query:
        search_words = search_query.split()  # 검색어를 공백 기준으로 나눔
        q_objects = Q()  # 빈 Q 객체 생성

        for word in search_words:
            q_objects &= (Q(title__icontains=word) | 
                          Q(location__icontains=word) |
                          Q(location_detail__icontains=word))

        posts_queryset = posts_queryset.filter(q_objects)

    # 내림차순 정렬 (작성일자를 기준으로 정렬한다고 가정)
    posts_queryset = posts_queryset.order_by('-created_at')  # 작성일자를 기준으로 내림차순 정렬



    # 페이지네이션 추가 (페이지당 10개의 게시글)
    paginator = Paginator(posts_queryset, 10)  # 페이지당 10개씩
    page_number = request.GET.get('page')  # URL에서 'page' GET 파라미터 가져오기
    page_obj = paginator.get_page(page_number)  # 해당 페이지의 게시글 가져오기

    # current_page = page_obj.number
    # total_pages = paginator.num_pages

    # # 양옆으로 보여줄 페이지 번호 범위 설정
    # page_range = range(max(current_page - 5, 1), min(current_page + 6, total_pages + 1))

    context = {
        'posts': page_obj,  # 필터링된 쿼리셋을 페이지네이션된 객체로 전달
        'selected_city': selected_city,
        'selected_district': selected_district,
        'district_list': district_list,
        'search_query': search_query,  # 검색 쿼리도 전달
        'page_obj': page_obj,  # 페이지네이션 객체 추가
        # 'page_range': page_range,  # 페이지 번호 범위 추가
    }

    return render(request, 'board/board.html', context)



from django.shortcuts import render

def Post_Writing_Page(request):
    var_name = request.user.name  # 로그인된 유저의 이름

    # 선택된 도시와 구/군을 GET 요청에서 가져옵니다.
    selected_city = request.GET.get('city')
    selected_district = request.GET.get('district')

    # 각 도시별로 구/군 목록을 딕셔너리로 정의
    districts = {
        "서울특별시": ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"],
        "경기도": ["가평군", "고양시", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시", "부천시", "성남시", "수원시", "시흥시", "안산시", "안성시", "안양시", "양주시", "양평군", "여주시", "연천군", "오산시", "용인시", "의왕시", "의정부시", "파주시", "평택시", "포천시", "하남시", "화성시"],
        "인천": ["강화군", "계양구", "남동구", "동구", "미추홀구", "부평구", "서구", "연수구", "옹진군", "중구"],
        "부산": ["강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구"],
        "대전": ["서구", "유성구", "대덕구", "동구", "중구"],
        "대구": ["중구", "동구", "서구", "남구", "달서구", "달성군", "북구", "수성구"],
        "울산": ["남구", "북구", "중구", "울주군"],
        "세종": ["고운동", "나성동", "다정동", "대평동", "도담동", "보람동", "새롬동", "소담동", "아름동", "어진동", "연기면", "연동면", "전의면", "조치원읍", "종촌동", "한솔동"],
        "광주": ["동구", "서구", "남구", "북구", "광산구"],
        "강원도": ["강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "평창읍", "홍천군", "화천군", "횡성군"],
        "충청북도": ["괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청주시", "충주시"],
        "충청남도": ["계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천군", "아산시", "예산군", "천안시", "청양군", "태안군", "홍성군"],
        "경상북도": ["경산시", "경주시", "고령군", "구미시", "군위군", "김천시", "문경시", "봉화군", "상주시", "성주군", "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡군", "포항시"],
        "경상남도": ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시", "통영시", "하동군", "함안군", "함양군", "합천군"],
        "전라북도": ["고창군", "군산시", "김제시", "남원시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군", "장수군", "전주시", "정읍시", "진안군"],
        "전라남도": ["강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군"],
        "제주": ["서귀포시", "제주시"]
    }

    # 선택된 도시의 구/군 리스트를 가져옵니다.
    district_list = districts.get(selected_city, [])

    # 선택된 구/군과 도시에 맞는 충전소 데이터를 필터링합니다.

    context = {
        'name': var_name,
        'selected_city': selected_city,
        'selected_district': selected_district,
        'district_list': district_list,
    }

    return render(request, 'board/post_writing.html', context)



def Post_Writing_Action(request):
    var_title = request.POST.get('input_title')
    var_content = request.POST.get('input_content')
    var_author = request.POST.get('input_author')
    var_city = request.POST.get('input_city')
    var_district = request.POST.get('input_district')
    image = request.FILES.get('input_image')  # 업로드된 이미지 가져오기
    user_object = Users.objects.get(id = request.user.id)
    
    if var_title and var_content:

        Posts.objects.create(
            title = var_title,
            content = var_content,
            author = var_author,
            connected_user = user_object,
            location = var_city,
            location_detail = var_district,
            image=image  # 이미지 저장

        )

    else:
        return redirect('게시판 글쓰기')
        
    return redirect('게시판')
    
#게시글 자세히 보기
def Post_Detail_Page(request, post_id):
    post_object = Posts.objects.get(id = post_id)

    return render(request, 'board/post_detail.html', {'post': post_object,'admin':admin})

#게시글 삭제
def delete_post(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    if request.method == "POST":
        # 게시글 작성자인지 확인
        if post.connected_user == request.user or request.user.id == admin:
            post.delete()
            messages.success(request, "게시글이 삭제되었습니다.")
        else:
            messages.error(request, "게시글을 삭제할 권한이 없습니다.")
    return redirect('게시판')  # 게시판으로 리디렉션

#게시글 수정
def change_post(request,post_id):
    var_name = request.user.name  # 로그인된 유저의 이름
    var_posts = request.user.posts.get(id=post_id)
    selected_city = request.GET.get('city',var_posts.location)
    selected_district = request.GET.get('district',var_posts.location_detail)

    # 각 도시별로 구/군 목록을 딕셔너리로 정의
    districts = {
        "서울특별시": ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"],
        "경기도": ["가평군", "고양시", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시", "부천시", "성남시", "수원시", "시흥시", "안산시", "안성시", "안양시", "양주시", "양평군", "여주시", "연천군", "오산시", "용인시", "의왕시", "의정부시", "파주시", "평택시", "포천시", "하남시", "화성시"],
        "인천": ["강화군", "계양구", "남동구", "동구", "미추홀구", "부평구", "서구", "연수구", "옹진군", "중구"],
        "부산": ["강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구"],
        "대전": ["서구", "유성구", "대덕구", "동구", "중구"],
        "대구": ["중구", "동구", "서구", "남구", "달서구", "달성군", "북구", "수성구"],
        "울산": ["남구", "북구", "중구", "울주군"],
        "세종": ["고운동", "나성동", "다정동", "대평동", "도담동", "보람동", "새롬동", "소담동", "아름동", "어진동", "연기면", "연동면", "전의면", "조치원읍", "종촌동", "한솔동"],
        "광주": ["동구", "서구", "남구", "북구", "광산구"],
        "강원도": ["강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "평창읍", "홍천군", "화천군", "횡성군"],
        "충청북도": ["괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청주시", "충주시"],
        "충청남도": ["계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천군", "아산시", "예산군", "천안시", "청양군", "태안군", "홍성군"],
        "경상북도": ["경산시", "경주시", "고령군", "구미시", "군위군", "김천시", "문경시", "봉화군", "상주시", "성주군", "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡군", "포항시"],
        "경상남도": ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시", "통영시", "하동군", "함안군", "함양군", "합천군"],
        "전라북도": ["고창군", "군산시", "김제시", "남원시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군", "장수군", "전주시", "정읍시", "진안군"],
        "전라남도": ["강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군"],
        "제주": ["서귀포시", "제주시"]
    }

    # 선택된 도시의 구/군 리스트를 가져옵니다.
    district_list = districts.get(selected_city, [])

    return render(request, 'board/post_change.html', {'name': var_name,
                                                      'posts' : var_posts,
                                                      'selected_city': selected_city,
                                                      'selected_district': selected_district,
                                                      'district_list': district_list,})

def change_post_action(request, post_id):
    post = get_object_or_404(Posts, id=post_id)  # 수정하려는 게시물을 가져옴
    var_title = request.POST.get('input_title')
    var_content = request.POST.get('input_content')
    var_author = request.POST.get('input_author')
    var_city = request.POST.get('input_city')
    var_district = request.POST.get('input_district')
    new_image = request.FILES.get('input_image')  # 새로 업로드된 이미지 가져오기
    user_object = Users.objects.get(id=request.user.id)

    # 입력된 제목과 내용이 있을 때만 게시물 수정 진행
    if var_title and var_content:
        post.title = var_title
        post.content = var_content
        post.author = var_author
        post.connected_user = user_object
        post.location = var_city
        post.location_detail = var_district
        
        # 새로운 이미지가 업로드되었을 경우에만 이미지 변경
        if new_image:
            post.image = new_image  # 새 이미지 저장
        # 이미지를 변경하지 않으면 기존 이미지를 그대로 유지

        post.save()  # 게시물 저장

    else:
        return redirect('게시글 수정')

    return redirect('게시판')


#내정보
def Myaccount_Page(request):
    var_posts = request.user.posts.all()

    return render(request, 'mypage/myacount.html', {'posts' : var_posts})

#내정보수정
def Edit_Info(request):
    var_name = request.POST.get('input_name')
    var_email = request.POST.get('input_email')
    var_address = request.POST.get('input_address')
    var_address_detail = request.POST.get('input_address_detail')

    if var_name and var_email:
            user = Users.objects.filter(id = request.user.id).first()
            user.name = var_name
            user.email = var_email
            user.address = var_address
            user.address_detail = var_address_detail
            user.save()

            return redirect('메인페이지')
    
    else:
        return redirect('내정보')

def User_Detail_Page(request, connected_user_id):
    user_object = Users.objects.get(id = connected_user_id)

    return render(request, 'user_detail.html', {'user' : user_object})


def Delete_Post(request, post_id):
    post_object = Posts.objects.get(id = post_id)
    post_object.delete()

    return redirect('게시판')

def Ev_cumminity_detail(request, station_name):
    csv_file_path = 'asdf/static/csv/병합된_충전소_데이터_UTF8.csv'
    
    # pandas를 사용하여 CSV 파일 읽기
    df = pd.read_csv(csv_file_path)
    
    # 선택한 충전소의 세부 정보 가져오기
    station_info = df[df['충전소명'] == station_name].iloc[0]

    return render(request, 'Ev_cumminity_detail.html', {'station_info': station_info})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Posts, Comment
from django.contrib.auth.decorators import login_required

#댓글
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # 댓글 생성
            Comment.objects.create(
                connected_post=post,
                user=request.user,
                content=content
            )
        return redirect('게시판 글정보', post_id=post.id)

#댓글삭제    
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.connected_post.id
    
    
    # 현재 사용자가 댓글 작성자인지 확인
    if request.user == comment.user or request.user.id == admin:
        post_id = comment.connected_post.id
        comment.delete()
        messages.success(request, "댓글이 삭제되었습니다.")
    else:
        messages.error(request, "댓글을 삭제할 권한이 없습니다.")
    
    return redirect('게시판 글정보', post_id=post_id)



def location_page(request):
    return render(request, 'location.html')








