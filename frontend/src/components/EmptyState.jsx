export default function EmptyState({ title, action }) {
  return (
    <div className="card text-center py-12">
      <h3 className="text-lg text-slate-300">{title}</h3>
      <p className="text-sm text-slate-500 mt-2">Generate demo data from the Demo Control panel to populate the workstation.</p>
      {action}
    </div>
  )
}
