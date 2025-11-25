/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Composables
import { createVuetify } from 'vuetify'
// Styles
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#4e9d2d',
          secondary: '#1d5632',
          accent: '#c4d600'
        }
      },
      dark: {
        colors: {
          primary: '#4e9d2d',
          secondary: '#1d5632',
          accent: '#c4d600'
        }
      }
    }
  },
})
