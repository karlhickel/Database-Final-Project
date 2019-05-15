import { drawBarChart, drawPieChart } from '/static/financeManager/js/charts.js';
google.charts.load("current", {packages:["corechart"]});
google.setOnLoadCallback(function () {
  drawBarChart({{ data.bar.neg }}, {{ data.bar.pos }})
});

console.log("got here")
