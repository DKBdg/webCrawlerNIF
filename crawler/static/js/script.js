var dropdown = 'login'

function show_alert(text,type='error',close_delay=3000){
  types={
    'error':'.request-error-block',
    'success':'.request-success-block'
  }
  var block = $(types[type]);
  block.find('div').html(text);
  block.slideDown(100);
  setTimeout(function(){
      block.slideUp(100);
  }, close_delay);
}

function make_ajax_json(new_args){
  var margs={
    url:"",
    data:'',
    final:function(){},
    success:function(){console.log("S")},
    fail:function(){}
  };

  margs.success=function(data, textStatus, jqXHR){
    if(jqXHR.responseJSON['success']){
      show_alert(jqXHR.responseJSON['msg'],'success');
    }else{
      show_alert(jqXHR.responseJSON['msg'],'error');
    }
    margs.final();
  };
  margs.fail=function(jqXHR, textStatus, errorThrown) {
    if(jqXHR.responseJSON){
      show_alert(jqXHR.responseJSON['msg'],'error');
    }
    margs.final();
  };
  Object.keys(new_args).forEach(function(key) {
    margs[key] = new_args[key];
  });
  console.log("=>",margs)
  $.ajax({
      type: "POST",
      url:margs.url ,
      dataType: "json",
      data:margs.data,
      success:margs['success'],
      error: margs['fail']
  });
}
$(window).ready(function () {
  $.ajaxSetup({
    headers: {
    "X-CSRFToken": document.querySelector('input[name=csrfmiddlewaretoken]').value,
    }
  });
  $(document).click(function(e){
    var main_div = $(".auth-block");
    var divs = [$(".auth-login-block"),$(".auth-register-block")];
    for (var i = divs.length - 1; i >= 0; i--) {
      if (!main_div.is(e.target) && main_div.has(e.target).length === 0){
        divs[i].slideUp(200);
      }
    }
  });
    $('.auth-block').hover(function () {
      $('.auth-profile-block.dropdown-content').slideDown(200);
    },function() {
      $('.auth-profile-block.dropdown-content').stop(true).delay(1000).slideUp(200);
    });

    $('.auth-block').hover(function () {
      $('.auth-'+dropdown+'-block.dropdown-content').slideDown(200);
    });
    $('.additional-input-link').click(function () {
      var el = $(this);
      if(el.attr('activity')==='close'){
        $('.additional-content-block.dropdown-content').slideUp(100);
        el.attr('activity','')
      }else{
        el.attr('activity','close');
        $('.additional-content-block.dropdown-content').slideDown(100);
      }

    });

    $('form#searchForm input[type=send]').click(function(event){
      //event.preventDefault();
      $(this).attr("disabled", true);
      make_ajax_json({
        url:search,
        data: $('form#searchForm').serialize(),
        final:function(){
          console.log("disable true")
          $('form#searchForm input[type=send]').attr("disabled", false);
        }
      });
    });

    $('form#downloadForm input[type=send]').click(function(event){
      $.ajax({
          type: "POST",
          url:download,
          data:$('form#downloadForm').serialize(),
          dataType:'json',
          success:function(data, textStatus, jqXHR) {
            console.log("data",jqXHR.responseJSON)
            if(jqXHR.responseJSON['success']){
              $('form#downloadForm').submit();
            }else{
              show_alert(data['msg'],'success');
            }
          },
          error:function(jqXHR, textStatus, errorThrown){show_alert(jqXHR.responseJSON['msg']);}
      });
    });
    $('#register-button').click(function(){
      dropdown='register'
      $('.auth-login-block.dropdown-content').css('display','none');
      $('.auth-register-block.dropdown-content').slideDown(200);
    });
    // $('.auth-register-form input[type=submit]').click(function(event){
    //   event.preventDefault();
    //   make_ajax_json({
    //     url:register,
    //     data:$('.auth-register-form').serialize()
    //   });
    // });
});
