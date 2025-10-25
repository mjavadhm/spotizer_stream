<script lang="ts">
  import type { Track } from '$lib/types';

  export let track: Track | null;

  let audio: HTMLAudioElement;
  let isPlaying = false;
  let currentTime = 0;
  let duration = 0;

  $: if (track && audio) {
    audio.src = `https://api.javadhm.online/stream/track/${track.id}`;
    audio.play().catch(e => console.error("Playback failed:", e));
  }

  function togglePlay() {
    if (!audio) return;
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
  }

  function handleSeek(e: Event) {
    const target = e.target as HTMLInputElement;
    if (!audio) return;
    audio.currentTime = Number(target.value);
  }

  function formatTime(seconds: number) {
    if (isNaN(seconds)) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  }
</script>

<style>
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    background: #3b82f6;
    border-radius: 50%;
    cursor: pointer;
    transition: background 0.2s;
  }
  input[type=range]::-webkit-slider-thumb:hover {
    background: #2563eb;
  }
</style>

{#if track}
<div class="fixed bottom-0 left-0 right-0 p-4 bg-gray-800 shadow-lg border-t border-gray-700">
  <div class="flex items-center space-x-4 max-w-4xl mx-auto">
    <div class="flex-grow min-w-0">
      <p class="font-bold truncate">{track.title}</p>
      <p class="text-sm text-gray-400 truncate">{track.artist}</p>
    </div>

    <div class="flex items-center space-x-3">
      <button on:click={togglePlay} class="p-2 text-white bg-blue-600 rounded-full hover:bg-blue-700 transition-transform transform hover:scale-110">
        {#if isPlaying}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        {/if}
      </button>

      <div class="flex items-center space-x-2 text-sm">
        <span class="w-10 text-right">{formatTime(currentTime)}</span>
        <input
          type="range"
          value={currentTime}
          on:change={handleSeek}
          on:input={e => currentTime = Number(e.currentTarget.value)}
          max={duration || 0}
          class="w-48 h-1 bg-gray-600 rounded-full appearance-none cursor-pointer"
        />
        <span class="w-10">{formatTime(duration)}</span>
      </div>
    </div>
  </div>
</div>
{/if}

<audio
  bind:this={audio}
  bind:currentTime
  bind:duration
  on:play={() => isPlaying = true}
  on:pause={() => isPlaying = false}
  on:ended={() => isPlaying = false}
></audio>
