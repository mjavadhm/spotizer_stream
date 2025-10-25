<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { fetchTracks } from '$lib/api';
  import type { Track } from '$lib/types';
  import Player from '$lib/components/Player.svelte';

  let userId = '';
  let playlistId = '';
  let tracks: Track[] = [];
  let currentTrack: Track | null = null;
  let error: string | null = null;
  let isLoading = false;
  let pageLoading = true;
  let pollingInterval: any = null;

  onMount(() => {
    const timer = setTimeout(() => {
      pageLoading = false;
    }, 1500);
    return () => clearTimeout(timer);
  });

  onDestroy(() => {
    stopPolling();
  });

  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  }

  function startPolling() {
    stopPolling();
    pollingInterval = setInterval(async () => {
      try {
        const currentId = userId || playlistId;
        const currentType = userId ? 'user' : 'playlist';
        if (!currentId) return stopPolling();

        const updatedTracks = await fetchTracks(currentId, currentType);
        tracks = updatedTracks;

        const allReady = updatedTracks.every(track => track.file_id);
        if (allReady) {
          stopPolling();
        }
      } catch (e) {
        console.error('Polling failed:', e);
      }
    }, 10000);
  }

  function triggerError(message: string) {
    error = message;
    setTimeout(() => {
      error = null;
    }, 5000);
  }

  async function handleSubmit() {
    isLoading = true;
    error = null;
    tracks = [];
    currentTrack = null;
    stopPolling();

    try {
      if (!userId && !playlistId) return;
      const id = userId || playlistId;
      const type = userId ? 'user' : 'playlist';
      tracks = await fetchTracks(id, type);

      const someProcessing = tracks.some(track => !track.file_id);
      if (someProcessing) {
        startPolling();
      }
    } catch (e) {
      triggerError('Failed to fetch tracks. Please check the ID and try again.');
    } finally {
      isLoading = false;
    }
  }

  function playTrack(track: Track) {
    if (track.file_id) {
      currentTrack = track;
    }
  }
</script>

<div class="flex flex-col items-center justify-center min-h-screen p-4 pb-24">
  {#if pageLoading}
    <div in:fade={{ duration: 500 }} class="flex flex-col items-center space-y-4">
      <svg class="w-16 h-16 text-blue-500 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-lg font-semibold">Loading...</span>
    </div>
  {:else if tracks.length === 0}
    <div in:fade={{ duration: 500 }} class="w-full max-w-md p-8 space-y-8 bg-gray-800 rounded-lg shadow-lg">
      <h1 class="text-3xl font-bold text-center text-white">Music Streamer</h1>
      <form on:submit|preventDefault={handleSubmit} class="space-y-6">
        <div>
          <label for="userId" class="block mb-2 text-sm font-medium text-gray-300">User ID</label>
          <input type="text" id="userId" bind:value={userId} disabled={!!playlistId} class="w-full px-4 py-2 text-white bg-gray-700 border border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50" placeholder="Enter User ID"/>
        </div>
        <div class="text-center text-gray-400">OR</div>
        <div>
          <label for="playlistId" class="block mb-2 text-sm font-medium text-gray-300">Playlist ID</label>
          <input type="text" id="playlistId" bind:value={playlistId} disabled={!!userId} class="w-full px-4 py-2 text-white bg-gray-700 border border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50" placeholder="Enter Playlist ID"/>
        </div>
        <button type="submit" class="w-full px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-500" disabled={(!userId && !playlistId) || isLoading}>
          {#if isLoading}
            <span class="animate-pulse">Fetching...</span>
          {:else}
            Fetch Tracks
          {/if}
        </button>
        {#if error}
          <div in:fade={{ duration: 300 }} out:fade={{ duration: 300 }}>
            <p class="p-2 mt-2 text-sm text-center text-white bg-red-500 rounded-md">{error}</p>
          </div>
        {/if}
      </form>
    </div>
  {:else}
    <div class="w-full max-w-2xl p-4 bg-gray-800 rounded-lg shadow-lg" in:fly={{ y: 20, duration: 500 }}>
      <h2 class="mb-4 text-2xl font-bold">Track List</h2>
      <ul class="space-y-2">
        {#each tracks as track (track.id)}
          <li
            class="flex items-center p-3 transition-colors duration-200 rounded-md"
            class:bg-gray-700={track.file_id}
            class:bg-gray-600={!track.file_id}
            class:opacity-50={!track.file_id}
            class:cursor-pointer={track.file_id}
            class:hover:bg-blue-500={track.file_id}
            on:click={() => playTrack(track)}
          >
            <div class="flex-grow">
              <p class="font-semibold">{track.title || 'Unknown Title'}</p>
              <p class="text-sm text-gray-400">{track.artist || 'Unknown Artist'}</p>
            </div>
            {#if !track.file_id}
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-400">Processing...</span>
                <svg class="w-5 h-5 text-blue-400 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
            {/if}
          </li>
        {/each}
      </ul>
    </div>
  {/if}
</div>

<Player bind:track={currentTrack} />
