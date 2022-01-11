import { createWebHistory, createRouter } from 'vue-router'

import Home from '@/components/Home.vue'
import DisplayAllPlays from '@/components/DisplayAllPlays.vue'
import ConfigureGame from '@/components/ConfigureGame.vue'
import ConfigureTeam from '@/components/ConfigureTeam.vue'
import PlayGame from '@/components/PlayGame.vue'

const routes = [
    { path: '/', name: 'Home', component: Home },
    { path: '/game/configure', name: 'ConfigureGame', component: ConfigureGame },
    { path: '/team/configure', name: 'ConfigureTeam', component: ConfigureTeam, props: true },
    { path: '/game/load', name: 'Load Game'},
    { path: '/game/', name: 'PlayGame', component: PlayGame, props: true },
    { path: '/plays/all', name: 'DisplayAllPlays', component: DisplayAllPlays }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
