from app.domain import StoryFlavor


BASE_WPM = 150

flavour_to_wpm: dict[StoryFlavor, float] = {
    StoryFlavor.FAIRY_TALE: 0.95 * BASE_WPM,
    StoryFlavor.THRILLER: 0.90 * BASE_WPM,
    StoryFlavor.ROMANCE: 0.95 * BASE_WPM,
    StoryFlavor.SCIENCE_FICTION: 0.98 * BASE_WPM,
}
