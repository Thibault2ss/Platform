$(function() {

  var $table = $('#tablgngfhdwe').tablesorter({
    // theme: 'blue',
    widgets: ["filter"],
    widgetOptions : {
      // filter_anyMatch replaced! Instead use the filter_external option
      // Set to use a jQuery selector (or jQuery object) pointing to the
      // external filter (column specific or any match)
      filter_external : '.search',
      // add a default type search to the first name column
    //   filter_defaultFilter: { 1 : '~{query}' },
      // include column filters

      filter_columnFilters: true,
      filter_placeholder: { search : 'Search...' },

      filter_saveFilters : true,
      filter_reset: '.reset'
    }
  });

  $('button[data-column]').on('click', function(){
      var $this = $(this),
        totalColumns = $table[0].config.columns,
        col = $this.data('column'), // zero-based index or "all"
        filter = [];

      // text to add to filter
      filter[ col === 'all' ? totalColumns : col ] = $this.text();
      $table.trigger('search', [ filter ]);
      return false;
    });

  // // $.tablesorter.filter.bindSearch( $table, $('#search-1') );
  // alert("loaded");
  // // make demo search buttons work
  // $('.search').on('input', function(){
  //   var $this = $(this),
  //     totalColumns = $table[0].config.columns,
  //     col = $this.data("all"), // datatitle of column, zero-based index or "all"
  //     filter = [];
  //     console.log(totalColumns.toString());
  //   //   alert("test is:" + $this.val());
  //   // text to add to filter
  //   filter[ 1 ] = $this.val();
  //   console.log("filter is " +filter.toString());
  //   $table.trigger('search', [ filter ]);
  //   console.log("test1: " + $this.val());
  //   return false;
  // });

});
