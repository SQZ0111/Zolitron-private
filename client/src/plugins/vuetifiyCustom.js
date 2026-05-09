import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

const blueSkyTheme = {
  defaultTheme: 'blueSky',
  themes: {
    blueSky: {
      colors: {
        primary: '#1E88E5',
        secondary: '#42A5F5',
        accent: '#FFA726',
        background: '#F5F9FF',
        surface: '#FFFFFF',
        error: '#EF5350',
        info: '#29B6F6',
        success: '#66BB6A',
        warning: '#FFCA28',
        blue50: '#E3F2FD',
        blue100: '#BBDEFB',
        blue200: '#90CAF9',
        blue300: '#64B5F6',
        blue400: '#42A5F5',
        blue500: '#2196F3',
        blue600: '#1E88E5',
        blue700: '#1976D2',
        blue800: '#1565C0',
        blue900: '#0D47A1',
        blue950: '#0A3D91'
      }
    }
  }
}

const vuetify = createVuetify({
  components,  
  directives,  
  theme: blueSkyTheme
})

export default vuetify