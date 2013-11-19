function convertDataTime(data) {
    for(datum in data) {
        data[datum][0] = data[datum][0] * 1000;
    }
    return data;
}

$(document).ready(function() {
    baseurl = "output/sample/";
    
    $.getJSON(baseurl+"gold.json", function(data) {
        console.log(data);
        
        // Create the chart
        $('#team_gold_chart').highcharts('StockChart', {
            

            rangeSelector : {
                buttons: [{ type: 'minute', count: '3', text: '3m'}, { type: 'minute', count: '10', text: '10m'}, {type : 'all', text : "All"}],
                inputEnabled: false
            },

            title : {
                text : 'Gold over time'
            },
            
            xAxis: {
                type : 'datetime'
            },
            
            tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%H:%M:%S', this.x) +'</b>';
    
                    $.each(this.points, function(i, point) {
                        s += '<br/>'+ this.series.name + ": " + Math.round(point.y);
                    });
                
                    return s;
                }
            },
            
            credits : false, 
            
            yAxis: [
                {
                    title : { text: "Total" },
                    min : 0,
                    height: 250,
                    lineWidth: 2
                },
                {
                    title : { text: "Difference" },
                    height: 150,
                    top: 325,
                    offset: 0,
                    lineWidth: 2,
                    plotBands: [{
                      from: 0,
                      to: 10000000,
                      color: '#AAD9FF'
                    },
                    {
                      from: -10000000,
                      to: 0,
                      color: '#B1AAFF'
                    }]
                }
                ],
            
            series : [
                {
                    name : 'Blue Team',
                    data : convertDataTime(data['teams'][0]),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#0046AF"
                },
                {
                    name : 'Purple Team',
                    data : convertDataTime(data['teams'][1]),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#7000AD"
                },
                {
                    name : 'Difference',
                    type : 'area',
                    fillColor : "rgba(0, 0, 0, 0.5)",
                    data : convertDataTime(data['difference']),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#000",
                    yAxis: 1
                }
            ]
        });
    });
});
