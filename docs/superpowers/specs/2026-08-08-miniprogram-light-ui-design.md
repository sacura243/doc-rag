# Mini Program Light UI Design

## Goal

Refine the existing knowledge-base mini program so it feels clean, dependable, and professional on mobile. Preserve all product behavior: login, administrator permissions, CloudBase upload, document import, deletion, index rebuild, and RAG questions.

## Visual Direction

- Light, cool-gray page background with white content surfaces.
- Muted teal is the sole primary accent; pale mint supports upload and empty states.
- Deep gray-green text with restrained contrast hierarchy.
- Consistent 10-14rpx corner-radius scale, thin borders, and no decorative shadows.
- Dense enough for repeated work, without turning sections into stacked decorative cards.

## Homepage

- Keep the brand and role indicator compact to prioritize the question workspace.
- Make the question composer the primary focus: clear title, concise helper text, comfortable text area, compact suggestion chips, and a full-width centered primary action.
- Present Upload and Document Management as aligned shortcut rows with fixed icon, title, supporting count, and arrow positions.
- Use structured statistics and a readable recent-document list with file-type indicators rather than additional visual decoration.
- Keep the existing loading, error, answer, source, and empty states visible and understandable.

## Documents Page

- Use a pale-mint upload panel that states supported file formats and presents Upload as the primary action.
- Keep Rebuild Index as a secondary action to reduce accidental use.
- Structure each document row around file type, name, chunk count, and an isolated destructive action.
- Retain a clear empty state with a direct upload action.

## Interaction Rules

- Native button labels must be vertically and horizontally centered after WeChat default styles are neutralized.
- Touch targets must retain stable dimensions and readable text on narrow devices.
- Do not add unsupported local-file picker behavior; document upload continues to follow WeChat's file-selection constraints.

## Verification

- Existing mini-program automated tests must pass.
- Add focused regression tests for any behavior-affecting changes.
- Inspect both pages in the WeChat Developer Tools simulator and verify the centered action controls on a narrow device profile.
