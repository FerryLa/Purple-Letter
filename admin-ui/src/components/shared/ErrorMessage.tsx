import { AlertCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

interface ErrorMessageProps {
  title?: string
  message?: string
}

export function ErrorMessage({
  title = '오류 발생',
  message = '데이터를 불러오는 중 오류가 발생했습니다.',
}: ErrorMessageProps) {
  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  )
}
