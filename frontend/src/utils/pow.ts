/**
 * Client-side Proof of Work Solver
 * Solves SHA-256 based PoW challenges by finding a nonce that produces
 * a hash with the required number of leading zero bits.
 */

/**
 * Count leading zero bits in a hash
 */
function countLeadingZeroBits(hash: Uint8Array): number {
  let zeroBits = 0
  for (const byte of hash) {
    if (byte === 0) {
      zeroBits += 8
    } else {
      // Count leading zero bits in this byte
      for (let i = 7; i >= 0; i--) {
        if ((byte & (1 << i)) === 0) {
          zeroBits++
        } else {
          return zeroBits
        }
      }
    }
  }
  return zeroBits
}

/**
 * Solve a proof of work challenge
 * @param prefix - The challenge prefix to prepend to the nonce
 * @param difficulty - Number of leading zero bits required
 * @param onProgress - Progress callback (0-1)
 * @returns The nonce that solves the challenge
 */
export async function solveProofOfWork(
  prefix: string,
  difficulty: number,
  onProgress?: (progress: number) => void
): Promise<string> {
  const encoder = new TextEncoder()
  const prefixBytes = encoder.encode(prefix)
  
  // Estimate iterations based on difficulty (2^difficulty on average)
  const estimatedIterations = Math.pow(2, difficulty)
  const progressInterval = Math.max(1000, Math.floor(estimatedIterations / 100))
  
  let nonce = 0
  const maxIterations = Math.pow(2, 32) // Safety limit
  
  while (nonce < maxIterations) {
    // Create the message: prefix + nonce
    const nonceStr = nonce.toString()
    const nonceBytes = encoder.encode(nonceStr)
    
    // Combine prefix and nonce
    const message = new Uint8Array(prefixBytes.length + nonceBytes.length)
    message.set(prefixBytes, 0)
    message.set(nonceBytes, prefixBytes.length)
    
    // Hash the message
    const hashBuffer = await crypto.subtle.digest('SHA-256', message)
    const hashBytes = new Uint8Array(hashBuffer)
    
    // Check if we have enough leading zeros
    const zeroBits = countLeadingZeroBits(hashBytes)
    
    if (zeroBits >= difficulty) {
      // Found a solution!
      return nonceStr
    }
    
    nonce++
    
    // Report progress periodically
    if (onProgress && nonce % progressInterval === 0) {
      // Progress is based on probability of finding solution
      const expectedProgress = Math.min(1, nonce / estimatedIterations)
      onProgress(expectedProgress)
      
      // Yield to the event loop to keep UI responsive
      await new Promise(resolve => setTimeout(resolve, 0))
    }
  }
  
  throw new Error('Failed to solve proof of work challenge')
}

/**
 * Verify a proof of work solution (for debugging)
 */
export async function verifyProofOfWork(
  prefix: string,
  nonce: string,
  difficulty: number
): Promise<boolean> {
  const encoder = new TextEncoder()
  const message = encoder.encode(prefix + nonce)
  const hashBuffer = await crypto.subtle.digest('SHA-256', message)
  const hashBytes = new Uint8Array(hashBuffer)
  const zeroBits = countLeadingZeroBits(hashBytes)
  return zeroBits >= difficulty
}
