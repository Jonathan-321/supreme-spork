/**
 * Enhanced Visualizations for AgriFinanceIntelligence
 * This file contains advanced chart configurations and data visualization helpers
 */

// Configuration for color schemes
const colorSchemes = {
  primary: ['#198754', '#20c997', '#0dcaf0', '#0d6efd', '#6610f2', '#6f42c1'],
  climate: ['#0d6efd', '#0dcaf0', '#20c997', '#198754', '#ffc107', '#fd7e14', '#dc3545'],
  credit: ['#198754', '#20c997', '#0dcaf0', '#6c757d', '#dc3545'],
  sequential: ['#73c3ff', '#45b6fe', '#0d6efd', '#0a58ca', '#084298', '#052c65'],
  diverging: ['#dc3545', '#e35d6a', '#ea858f', '#f1aeb5', '#d3d3d3', '#a7d7ff', '#79caff', '#0dcaf0', '#0d6efd']
};

/**
 * Creates an enhanced weather chart with temperature and precipitation data
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} dates - Array of date strings
 * @param {Array} temperatures - Array of temperature values
 * @param {Array} precipitation - Array of precipitation values
 */
function createWeatherChart(canvasId, dates, temperatures, precipitation) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  // Calculate moving averages for smoother lines
  const tempMA = calculateMovingAverage(temperatures, 3);
  
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        {
          label: 'Temperature (°C)',
          data: temperatures,
          borderColor: colorSchemes.climate[2],
          backgroundColor: hexToRgba(colorSchemes.climate[2], 0.1),
          borderWidth: 2,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 5,
          yAxisID: 'y',
          fill: true
        },
        {
          label: 'Temperature Trend',
          data: tempMA,
          borderColor: colorSchemes.climate[3],
          borderWidth: 3,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 0,
          yAxisID: 'y',
          borderDash: [5, 5],
          fill: false
        },
        {
          label: 'Precipitation (mm)',
          data: precipitation,
          type: 'bar',
          backgroundColor: hexToRgba(colorSchemes.climate[0], 0.6),
          borderColor: colorSchemes.climate[0],
          borderWidth: 1,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 10
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                label += ': ';
              }
              if (context.parsed.y !== null) {
                if (context.datasetIndex === 2) {
                  label += context.parsed.y + ' mm';
                } else {
                  label += context.parsed.y + ' °C';
                }
              }
              return label;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            maxTicksLimit: 10
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Temperature (°C)'
          },
          grid: {
            borderDash: [2, 2]
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Precipitation (mm)'
          },
          grid: {
            drawOnChartArea: false
          },
          min: 0
        }
      }
    }
  });
  
  return chart;
}

/**
 * Creates an enhanced NDVI chart with trend analysis
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} dates - Array of date strings
 * @param {Array} ndviValues - Array of NDVI values
 */
function createNDVIChart(canvasId, dates, ndviValues) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  // Calculate trend
  const trend = calculateLinearRegression(ndviValues);
  const trendLine = dates.map((_, i) => trend.slope * i + trend.intercept);
  
  // Calculate health zones
  const healthZones = [
    { value: 0.2, color: '#dc3545', label: 'Poor' },
    { value: 0.4, color: '#fd7e14', label: 'Fair' },
    { value: 0.6, color: '#ffc107', label: 'Good' },
    { value: 0.8, color: '#20c997', label: 'Very Good' },
    { value: 1.0, color: '#198754', label: 'Excellent' }
  ];
  
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        {
          label: 'NDVI Values',
          data: ndviValues,
          borderColor: colorSchemes.primary[0],
          backgroundColor: hexToRgba(colorSchemes.primary[0], 0.1),
          borderWidth: 2,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: function(context) {
            const value = context.raw;
            for (let i = 0; i < healthZones.length; i++) {
              if (value <= healthZones[i].value) {
                return healthZones[i].color;
              }
            }
            return healthZones[healthZones.length - 1].color;
          },
          fill: true
        },
        {
          label: 'Trend',
          data: trendLine,
          borderColor: '#6c757d',
          borderWidth: 2,
          borderDash: [5, 5],
          tension: 0,
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 10
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                label += ': ';
              }
              if (context.parsed.y !== null) {
                label += context.parsed.y.toFixed(2);
                
                // Add vegetation health status
                if (context.datasetIndex === 0) {
                  const value = context.parsed.y;
                  for (let i = 0; i < healthZones.length; i++) {
                    if (value <= healthZones[i].value) {
                      label += ` (${healthZones[i].label})`;
                      break;
                    }
                  }
                }
              }
              return label;
            }
          }
        },
        annotation: {
          annotations: {
            poor: {
              type: 'line',
              yMin: 0.2,
              yMax: 0.2,
              borderColor: healthZones[0].color,
              borderWidth: 1,
              borderDash: [2, 2],
              label: {
                content: 'Poor',
                enabled: true,
                position: 'left'
              }
            },
            fair: {
              type: 'line',
              yMin: 0.4,
              yMax: 0.4,
              borderColor: healthZones[1].color,
              borderWidth: 1,
              borderDash: [2, 2],
              label: {
                content: 'Fair',
                enabled: true,
                position: 'left'
              }
            },
            good: {
              type: 'line',
              yMin: 0.6,
              yMax: 0.6,
              borderColor: healthZones[2].color,
              borderWidth: 1,
              borderDash: [2, 2],
              label: {
                content: 'Good',
                enabled: true,
                position: 'left'
              }
            },
            veryGood: {
              type: 'line',
              yMin: 0.8,
              yMax: 0.8,
              borderColor: healthZones[3].color,
              borderWidth: 1,
              borderDash: [2, 2],
              label: {
                content: 'Very Good',
                enabled: true,
                position: 'left'
              }
            }
          }
        }
      },
      scales: {
        y: {
          min: 0,
          max: 1,
          title: {
            display: true,
            text: 'NDVI Value'
          }
        }
      }
    }
  });
  
  return chart;
}

/**
 * Creates an enhanced credit score radar chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Component labels
 * @param {Array} values - Component values
 * @param {Array} weights - Component weights
 */
function createCreditScoreRadarChart(canvasId, labels, values, weights) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  // Calculate weighted values
  const weightedValues = values.map((val, i) => val * weights[i] * 100);
  
  // Calculate benchmark values (industry average)
  const benchmarkValues = weights.map(w => w * 0.7 * 100);
  
  const chart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Your Score',
          data: weightedValues,
          backgroundColor: hexToRgba(colorSchemes.primary[0], 0.2),
          borderColor: colorSchemes.primary[0],
          borderWidth: 2,
          pointBackgroundColor: colorSchemes.primary[0],
          pointRadius: 4
        },
        {
          label: 'Industry Average',
          data: benchmarkValues,
          backgroundColor: 'transparent',
          borderColor: '#6c757d',
          borderWidth: 1,
          borderDash: [5, 5],
          pointBackgroundColor: '#6c757d',
          pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 10
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                label += ': ';
              }
              if (context.parsed.r !== null) {
                // Convert back to original scale
                const originalValue = context.parsed.r / 100 / weights[context.dataIndex];
                label += originalValue.toFixed(2) + ' (weighted: ' + context.parsed.r.toFixed(1) + ')';
              }
              return label;
            }
          }
        }
      },
      scales: {
        r: {
          angleLines: {
            display: true,
            color: 'rgba(255, 255, 255, 0.1)'
          },
          suggestedMin: 0,
          suggestedMax: 30,
          ticks: {
            stepSize: 10,
            backdropColor: 'transparent'
          }
        }
      }
    }
  });
  
  return chart;
}

/**
 * Creates a loan status distribution chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} statusData - Object with loan status counts
 */
function createLoanStatusChart(canvasId, statusData) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  const statusColors = {
    'PENDING': '#6c757d',
    'APPROVED': '#0dcaf0',
    'DISBURSED': '#0d6efd',
    'REPAYING': '#20c997',
    'COMPLETED': '#198754',
    'DEFAULTED': '#dc3545',
    'REJECTED': '#fd7e14'
  };
  
  const labels = Object.keys(statusData);
  const data = Object.values(statusData);
  const colors = labels.map(label => statusColors[label]);
  
  const chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderColor: '#2a2a2a',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            usePointStyle: true,
            boxWidth: 10
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.parsed || 0;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = Math.round((value * 100) / total);
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      },
      cutout: '70%'
    }
  });
  
  return chart;
}

/**
 * Creates a climate risk heatmap
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} risks - Array of risk objects
 */
function createClimateRiskHeatmap(canvasId, risks) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  // Process data for heatmap
  const riskTypes = [...new Set(risks.map(r => r.risk_type))];
  const regions = [...new Set(risks.map(r => r.region))];
  
  // Create data matrix
  const data = [];
  regions.forEach(region => {
    const row = [];
    riskTypes.forEach(riskType => {
      const risk = risks.find(r => r.region === region && r.risk_type === riskType);
      row.push(risk ? riskLevelToValue(risk.risk_level) : 0);
    });
    data.push(row);
  });
  
  const chart = new Chart(ctx, {
    type: 'matrix',
    data: {
      datasets: [{
        data: data.flat().map((value, i) => ({
          x: i % riskTypes.length,
          y: Math.floor(i / riskTypes.length),
          v: value
        })),
        backgroundColor(context) {
          const value = context.dataset.data[context.dataIndex].v;
          return getRiskColor(value);
        },
        borderColor: '#2a2a2a',
        borderWidth: 1,
        width: ({ chart }) => (chart.chartArea || {}).width / riskTypes.length - 1,
        height: ({ chart }) => (chart.chartArea || {}).height / regions.length - 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            title() {
              return '';
            },
            label(context) {
              const x = context.dataset.data[context.dataIndex].x;
              const y = context.dataset.data[context.dataIndex].y;
              const v = context.dataset.data[context.dataIndex].v;
              return [
                `Region: ${regions[y]}`,
                `Risk: ${riskTypes[x]}`,
                `Level: ${riskValueToLevel(v)}`
              ];
            }
          }
        },
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          type: 'category',
          labels: riskTypes,
          offset: true,
          ticks: {
            display: true
          },
          grid: {
            display: false
          }
        },
        y: {
          type: 'category',
          labels: regions,
          offset: true,
          ticks: {
            display: true
          },
          grid: {
            display: false
          }
        }
      }
    }
  });
  
  return chart;
}

/**
 * Creates a correlation matrix chart for credit factors
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} factors - Array of factor names
 * @param {Array} correlationMatrix - 2D array of correlation values
 */
function createCorrelationMatrix(canvasId, factors, correlationMatrix) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  const data = [];
  correlationMatrix.forEach((row, i) => {
    row.forEach((value, j) => {
      data.push({
        x: j,
        y: i,
        v: value
      });
    });
  });
  
  const chart = new Chart(ctx, {
    type: 'matrix',
    data: {
      datasets: [{
        data: data,
        backgroundColor(context) {
          const value = context.dataset.data[context.dataIndex].v;
          return getCorrelationColor(value);
        },
        borderColor: '#2a2a2a',
        borderWidth: 1,
        width: ({ chart }) => (chart.chartArea || {}).width / factors.length - 1,
        height: ({ chart }) => (chart.chartArea || {}).height / factors.length - 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            title() {
              return '';
            },
            label(context) {
              const x = context.dataset.data[context.dataIndex].x;
              const y = context.dataset.data[context.dataIndex].y;
              const v = context.dataset.data[context.dataIndex].v;
              return [
                `${factors[y]} × ${factors[x]}`,
                `Correlation: ${v.toFixed(2)}`
              ];
            }
          }
        },
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          type: 'category',
          labels: factors,
          offset: true,
          ticks: {
            display: true
          },
          grid: {
            display: false
          }
        },
        y: {
          type: 'category',
          labels: factors,
          offset: true,
          ticks: {
            display: true
          },
          grid: {
            display: false
          }
        }
      }
    }
  });
  
  return chart;
}

// Utility functions

/**
 * Calculates moving average for an array
 * @param {Array} data - Input data array
 * @param {number} windowSize - Size of moving average window
 * @returns {Array} - Moving average array
 */
function calculateMovingAverage(data, windowSize) {
  const result = [];
  
  for (let i = 0; i < data.length; i++) {
    if (i < windowSize - 1) {
      result.push(null);
      continue;
    }
    
    let sum = 0;
    for (let j = 0; j < windowSize; j++) {
      sum += data[i - j];
    }
    
    result.push(sum / windowSize);
  }
  
  return result;
}

/**
 * Calculates linear regression for an array
 * @param {Array} data - Input data array
 * @returns {Object} - Object with slope and intercept
 */
function calculateLinearRegression(data) {
  const n = data.length;
  let sumX = 0;
  let sumY = 0;
  let sumXY = 0;
  let sumXX = 0;
  
  for (let i = 0; i < n; i++) {
    sumX += i;
    sumY += data[i];
    sumXY += i * data[i];
    sumXX += i * i;
  }
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;
  
  return { slope, intercept };
}

/**
 * Converts hex color to rgba
 * @param {string} hex - Hex color code
 * @param {number} alpha - Alpha value
 * @returns {string} - RGBA color string
 */
function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Converts risk level to numeric value
 * @param {string} level - Risk level
 * @returns {number} - Numeric value
 */
function riskLevelToValue(level) {
  const levels = {
    'MINIMAL': 1,
    'LOW': 2,
    'MEDIUM': 3,
    'HIGH': 4,
    'EXTREME': 5
  };
  
  return levels[level] || 0;
}

/**
 * Converts numeric value to risk level
 * @param {number} value - Numeric value
 * @returns {string} - Risk level
 */
function riskValueToLevel(value) {
  const levels = ['NONE', 'MINIMAL', 'LOW', 'MEDIUM', 'HIGH', 'EXTREME'];
  return levels[value] || 'UNKNOWN';
}

/**
 * Gets color for risk value
 * @param {number} value - Risk value
 * @returns {string} - Color
 */
function getRiskColor(value) {
  const colors = [
    'rgba(200, 200, 200, 0.5)',  // None
    'rgba(32, 201, 151, 0.7)',   // Minimal
    'rgba(255, 193, 7, 0.7)',    // Low
    'rgba(253, 126, 20, 0.7)',   // Medium
    'rgba(220, 53, 69, 0.7)',    // High
    'rgba(108, 17, 40, 0.7)'     // Extreme
  ];
  
  return colors[value] || colors[0];
}

/**
 * Gets color for correlation value
 * @param {number} value - Correlation value
 * @returns {string} - Color
 */
function getCorrelationColor(value) {
  // Use diverging color scheme from -1 to 1
  if (value < 0) {
    const intensity = Math.min(1, Math.abs(value));
    return hexToRgba(colorSchemes.diverging[Math.floor(intensity * 4)], 0.7);
  } else {
    const intensity = Math.min(1, value);
    return hexToRgba(colorSchemes.diverging[Math.floor(intensity * 4) + 5], 0.7);
  }
}
