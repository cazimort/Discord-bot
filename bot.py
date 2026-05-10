@bot.command()
async def find4(ctx, nombre: int = 100):
    global is_searching
    if is_searching:
        await ctx.send("⚠️ Une recherche est déjà en cours !")
        return

    is_searching = True
    await ctx.send(f"🔍 Recherche intensive de **{nombre}** pseudos 4 caractères...")

    found = 0
    try:
        for _ in range(nombre):
            if not is_searching:
                break

            username = generate_4char()
            
            if await check_username_api(username):
                found += 1
                await ctx.send(f"🎉 **TROUVÉ !** `@{username}`")
                await send_webhook(username)
                await asyncio.sleep(1)

            await asyncio.sleep(1.2)
    finally:
        is_searching = False
        if found == 0:
            await ctx.send("❌ Aucun pseudo disponible trouvé sur cette session.\nC’est normal, les 4 lettres/chiffres sont très rares.")
        else:
            await ctx.send(f"✅ Recherche terminée — **{found}** pseudo(s) trouvé(s) !")