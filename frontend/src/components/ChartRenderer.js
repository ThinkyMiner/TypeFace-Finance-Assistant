import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function ChartRenderer({ chartConfig }) {
  if (!chartConfig) return null;

  const { type, title, labels, datasets } = chartConfig;

  // Chart.js configuration
  const chartData = {
    labels: labels,
    datasets: datasets.map((dataset, index) => ({
      label: dataset.label,
      data: dataset.data,
      backgroundColor: [
        'rgba(255, 107, 53, 0.8)',   // Coral orange
        'rgba(255, 165, 0, 0.8)',     // Orange
        'rgba(255, 140, 66, 0.8)',    // Light orange
        'rgba(255, 195, 113, 0.8)',   // Peach
        'rgba(255, 220, 170, 0.8)',   // Light peach
      ],
      borderColor: [
        'rgba(255, 107, 53, 1)',
        'rgba(255, 165, 0, 1)',
        'rgba(255, 140, 66, 1)',
        'rgba(255, 195, 113, 1)',
        'rgba(255, 220, 170, 1)',
      ],
      borderWidth: 2,
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
          weight: 'bold',
        },
        color: '#FF6B35',
      },
    },
    scales: type === 'pie' || type === 'doughnut' ? undefined : {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '$' + value.toFixed(0);
          }
        }
      }
    }
  };

  // Render appropriate chart type
  switch (type?.toLowerCase()) {
    case 'bar':
      return <Bar data={chartData} options={options} />;
    case 'line':
      return <Line data={chartData} options={options} />;
    case 'pie':
      return <Pie data={chartData} options={options} />;
    case 'doughnut':
      return <Doughnut data={chartData} options={options} />;
    default:
      return <div>Unsupported chart type: {type}</div>;
  }
}

export default ChartRenderer;
