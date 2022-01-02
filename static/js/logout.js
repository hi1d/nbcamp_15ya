function logout(){
    $.removeCookie('15ya_token', {path:'/'}); 
    window.location.replace('/login')
}
