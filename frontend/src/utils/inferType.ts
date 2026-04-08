import type { ColumnType } from '../types/sheet'

const BOOL_STRINGS = new Set(['yes', 'no', 'true', 'false'])

export function inferType(values: unknown[]): ColumnType {
    let total = 0
    let boolCount = 0
    let dateCount = 0
    let numberCount = 0

    for (const v of values) {
        if (v === '' || v == null) continue
        total++

        // Only actual JS booleans or known bool strings — NOT 0/1
        if (typeof v === 'boolean') boolCount++
        if (typeof v === 'string' && BOOL_STRINGS.has(v.toLowerCase())) boolCount++

        if (v instanceof Date && !isNaN(v.getTime())) dateCount++
        if (typeof v === 'number' && !isNaN(v)) numberCount++
    }

    if (total === 0) return 'string'

    const threshold = 0.8 * total
    if (boolCount >= threshold) return 'boolean'
    if (dateCount >= threshold) return 'date'
    if (numberCount >= threshold) return 'number'
    return 'string'
}