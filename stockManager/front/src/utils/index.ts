
export const colorFromValue = (value: number): string => {
    return value > 0 ? 'red' : value < 0 ? 'green' : 'black';
}