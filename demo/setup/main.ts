import { defineAppSetup } from '@slidev/types'

export default defineAppSetup(({ app, router }) => {
  // Register global components or plugins here
  
  // Add router hooks if needed
  router.beforeEach((to, from, next) => {
    // Custom navigation logic
    next()
  })
})