% rebase('tmpl/base.tpl')
<div id="chartview"></div>
<script>
function requestData() {
    $.ajax({
        url: '../getchartdata',
        success: function(point){
            console.log(point);
            var series = chart.series[0];
            chart.series[0].addPoint(point.ohlc, true, true);
            setTimeout(requestData, 1000);
        },
    });
}
$(function () {
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });
        // Create the chart

        Highcharts.stockChart('chartview', {
            chart: {
                events: {
                    //load: requestData
                        // set up the updating of the chart each second
                        load: function () {

                        var series = this.series[0];
                        var past_x = 0;
                        setInterval(function () {
                                $.ajax({
                                    url: '../getchartdata',
                                    dataType: "json",
                                    success: function(point){
                                        x = point.time;
                                        y = point.o;
                                        z = point.h;
                                        a = point.l;
                                        b = point.c;
                                        console.log(series.data);
                                        if(past_x == x){
                                            series.removePoint(series.data.length-1, true, false);
                                            series.addPoint([x, y, z, a, b], true, false);
                                        }else{
                                            past_x = x;
                                            series.addPoint([x, y, z, a, b], true, false);
                                        }
                                    },
                                });
                        }, 1000); 
                    } 
                }
            },

            rangeSelector: {
                buttons: [{
                    count: 1,
                    type: 'minute',
                    text: '1M'
                }, {
                    count: 5,
                    type: 'minute',
                     text: '5M'
                }, {
                    type: 'all',
                    text: 'All'
                }],
                    inputEnabled: false,
                    selected: 0
                },

                title: {
                    text: 'FX data'
                },

                exporting: {
                    enabled: false
                },
            series: [{
                  name: 'Random data',
                  type: 'candlestick',
                  data: (function () {
                          function aj(){
                          var result = $.ajax({
                                url: "../getchartpastdata",
                                dataType: "json",
                                async: false
                                }).responseText;
                                return result;
                            }
                          ohlc_text=aj();
                          ohlc_json=JSON.parse(ohlc_text);
                          console.log(ohlc_text);
                          return ohlc_json.ohlclist;

                          }())
                }]
        });
});
</script>
