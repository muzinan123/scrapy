+function ($) {
  $(function () {
    $("#repos").DataTable();

    function bl_link_bind(e){
         var method = $(this).data('method');
         var href = $(this).attr('href');
         var url = href.split("?");
         var action = url[0];
         var params = [];
         if (url.length == 2){
           params = url[1];
         }
      if ($(this).attr('id') == 'github'){
        window.open(href);
         } else {
           $.ajax({
             type: method,
             url: action,
             data: params,
             success: function(data){
               if (data.code == 200){
                 alert(data.msg);
                 location.reload();
               }else if (data.code == 404){
                 alert(data.msg);
               }else{
                 alert(data.msg);
                 location.reload();
               }
             }
            })
         }
        e.preventDefault();
    }
    $("#repos").delegate('a.link', 'click', bl_link_bind);
    
  });
}(window.jQuery);
