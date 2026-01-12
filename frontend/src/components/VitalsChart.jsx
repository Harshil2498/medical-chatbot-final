
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const VitalsChart = ({ data, dataKey, title, color, unit }) => {
  // Format data for chart
  const chartData = data.map(vital => ({
    date: new Date(vital.recorded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    value: vital[dataKey]
  })).filter(d => d.value != null);

  return (
    <div className="vitals-chart">
      <h4 className="chart-title">{title}</h4>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip 
            formatter={(value) => [`${value} ${unit}`, title]}
            contentStyle={{ fontSize: 12 }}
          />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke={color} 
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default VitalsChart;