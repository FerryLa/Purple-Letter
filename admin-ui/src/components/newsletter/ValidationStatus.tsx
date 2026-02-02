import { AlertCircle, CheckCircle2, Info } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import type { ValidationResult } from '@/types'

interface ValidationStatusProps {
  validation: ValidationResult
}

export function ValidationStatus({ validation }: ValidationStatusProps) {
  const { is_valid, warnings, recommendations } = validation

  return (
    <div className="space-y-3">
      {/* Main Status */}
      {is_valid ? (
        <Alert variant="success">
          <CheckCircle2 className="h-4 w-4" />
          <AlertTitle>준비 완료</AlertTitle>
          <AlertDescription>
            뉴스레터가 발행 준비가 되었습니다.
          </AlertDescription>
        </Alert>
      ) : (
        <Alert variant="warning">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>검토 필요</AlertTitle>
          <AlertDescription>
            뉴스레터 발행 전 아래 항목을 확인해 주세요.
          </AlertDescription>
        </Alert>
      )}

      {/* Warnings */}
      {warnings.length > 0 && (
        <Alert variant="warning">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>경고</AlertTitle>
          <AlertDescription>
            <ul className="list-disc list-inside space-y-1 mt-2">
              {warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>권장사항</AlertTitle>
          <AlertDescription>
            <ul className="list-disc list-inside space-y-1 mt-2">
              {recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}
