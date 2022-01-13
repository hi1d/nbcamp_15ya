$(document).ready(function(){
    close()
    $('#loading').hide()
    $('#result').hide()
})

function show(){
    $('#flower_modal_container').show()
}

function close(){
    $('#flower_modal_container').hide()
    $('#loading').hide()
    $('#result').hide()
    $('#1').show()
    $('#3').remove()


}

function open_file(){
    $("#file_up").trigger("click");
}

$('.modal_background').click(function() {
    close()
})

$('#close_icon').click(function() {
    close()
})

$('#flower_modal_container').on('scroll touchmove mousewheel', function(event) {

    event.preventDefault();
    event.stopPropagation();
    return false;
  
  });

function file_upload(){
    let file = $('#file_up')[0].files[0]
    let form_data = new FormData()

    form_data.append("file_give", file)

    $.ajax({
        type: "POST",
        url: "/flower",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            if (response['result']=='success'){
                $('#1').hide()
                $('#loading').show()
                setTimeout(() => result(response['img'], response['name']), 6000);
                
            }
        }
    });
}

function result(img,name){
    $('#result').show()
    $('#loading').hide()
    let temp_html = `
    <div id="3">
    <img id="result" src="${img}">
    <h2 id="name" style="margin-top:150px; color: burlywood">Your Flower is ${name} ! </h2>
    </div>`
    $('#2').append(temp_html)
}