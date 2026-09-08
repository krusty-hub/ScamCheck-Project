import { createFileRoute } from '@tanstack/react-router'
import { ScannerDemo } from '@/components/scanner'

export const Route = createFileRoute('/dashboard')({
  component: DashboardComponent,
})

function DashboardComponent() {
  return <ScannerDemo />
}