export function drawBarChart(barN, barP) {
  var data = google.visualization.arrayToDataTable([
    ["Element", "Avg", { role: "style" } ],
    ["Negative", barN, "red"],
    ["Positive", barP, "green"],
  ]);

  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1,
                   { calc: "stringify",
                     sourceColumn: 1,
                     type: "string",
                     role: "annotation" },
                   2]);

  // find which value is greater
  {% if data.bar.pos > data.bar.neg %}
    var max = barnN;
  {% else %}
    var max = barP;
  {% endif %}

  var options = {
    title: "Average Transactions",
    backgroundColor: 'transparent',
    width: $(window).width()*.3,
    height: $(window).height()*.5,
    hAxis: {viewWindow: {
      min: 0,
      max: max+100
    }},
    bar: {groupWidth: "95%"},
    legend: { position: "none" },
    isStacked: true
  };
  var chart = new google.visualization.BarChart(document.getElementById("barchart"));
  chart.draw(view, options);
}

// Draw the chart and set the chart values
export function drawPieChart() {
  // Define the chart to be drawn.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Element');
  data.addColumn('number', 'Percentage');
  {% for i in range %}
    data.addRows([
      ["{{data.pie.state|index:i}}", {{data.pie.count|index:i}}]
    ]);
  {% endfor %}
  // Optional; add a title and set the width and height of the chart
  var options = {
    title:'Transactions by State',
    backgroundColor: 'transparent',
    width: $(window).width()*.3,
    height: $(window).height()*.5,
   };

  // Display the chart inside the <div> element with id="piechart"
  var chart = new google.visualization.PieChart(document.getElementById('piechart'));
  chart.draw(data, options);
}
