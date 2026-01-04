$(document).ready(function() {

  $( "#txtSearch" ).autocomplete({

    source: function( request, response ) {
      var search = $('#txtSearch').val();
      var stuff = {
          'search': search,
          'csrfmiddlewaretoken': '{{ csrf_token }}'
      };
      $.ajax( {
        url: "/searchUsers/",
        dataType: "jsonp",
        data: stuff ,
        success: function( data ) {
          response( data );
        }
      });
    },

    minLength: 1,

    select: function( event, ui ) {
      var stuff = {
          'name': ui.item.label,
          'csrfmiddlewaretoken': '{{ csrf_token }}'
      };
      $.ajax( {
        url:"/getUserInfo/",
        dataType: "jsonp",
        data: stuff ,
        success: function( data ) {
        $('#tpID').val(data[1]);
        $('#gstin').val(data[2]);
        }
      });
    }
  });
});
