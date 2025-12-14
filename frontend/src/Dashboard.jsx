import { AreaChart, Area, ResponsiveContainer } from 'recharts';
const data = [{v:40},{v:30},{v:60},{v:50},{v:80},{v:70}];
export default function Dashboard() {
   return (
     <div>
       <h2 className="text-2xl font-bold mb-6">System Status: <span className="text-green-500">OPTIMAL</span></h2>
       <div className="h-64 bg-ops-800 rounded border border-slate-700 p-4">
         <ResponsiveContainer width="100%" height="100%">
           <AreaChart data={data}><Area type="monotone" dataKey="v" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.2} /></AreaChart>
         </ResponsiveContainer>
       </div>
     </div>
   )
}