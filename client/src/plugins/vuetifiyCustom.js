// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Zolitron
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

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
    },
    blueSkyNight: {
      dark: true,
      colors: {
        primary: '#42A5F5',
        secondary: '#1E88E5',
        accent: '#FFA726',
        background: '#0A1E3F',
        surface: '#14315C',
        error: '#EF5350',
        info: '#29B6F6',
        success: '#66BB6A',
        warning: '#FFCA28'
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