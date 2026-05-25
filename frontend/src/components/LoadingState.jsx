export default function LoadingState({ message = 'Loading surveillance data...' }) {
  return (
    <div className="flex items-center justify-center h-64 text-slate-500">
      <div className="animate-pulse">{message}</div>
    </div>
  )
}
