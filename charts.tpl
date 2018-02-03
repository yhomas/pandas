% rebase('base.tpl')
<div id="my-chart"></div>
<div id="container"></div>
<div id="color_div">test_color_div</div>
<script type="text/javascript">
new Highcharts.Chart({{ !chart }});
</script>
<script>
function requestData() {
    $.ajax({
        url: '127.0.0.1:9999/getchartdata',
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

        Highcharts.stockChart('container', {
            chart: {
                events: {
                    //load: requestData
                        // set up the updating of the chart each second
                        load: function () {

                        var series = this.series[0];
                        setInterval(function () {
                                $.ajax({
                                    url: '/getchartdata',
                                    dataType: "json",
                                    success: function(point){
                                        //var series = this.series[1];
                                        console.log(point);
                                        console.log(point.time);
                                        //series.addPoint(point.ohlc, true, true);
                                        var x = (new Date()).getTime(), // current time
                                        x = point.time;
                                        y = point.o;
                                        z = point.h;
                                        a = point.l;
                                        b = point.c;
                                        console.log(x);
                                        series.addPoint([x, y, z, a, b], true, true);
                                    },
                                });/*
                                var x = (new Date()).getTime(), // current time
                                y = Math.round(Math.random() * 100);
                                z = Math.round(Math.random() * 101);
                                a = Math.round(Math.random() * 102);
                                b = Math.round(Math.random() * 103);
                                console.log(x);
                                series.addPoint([x, y, z, a, b], true, true);*/
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
                    text: 'Live random data'
                },

                exporting: {
                    enabled: false
                },

                series: [{
                    name: 'Random data',
                    type: 'candlestick',
                    data: (function () {
                      // generate an array of random data
                          var data = [],
                          time = (new Date()).getTime(),
                          i;

                          for (i = -1; i <= 0; i += 1) {
                              data.push([
                                  time + i * 1000,
                                  Math.round(Math.random() * 100),
                                  Math.round(Math.random() * 101),
                                  Math.round(Math.random() * 102),
                                  Math.round(Math.random() * 103)
                              ]);
                          }
                          return data;
                  }())
                }]
        });
});
</script>
<script> $(function  ($) {   $("#color_div").css("border",  "1px  solid  red"); }); </script>
