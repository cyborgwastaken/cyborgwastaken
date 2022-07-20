/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memmove.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: gcyril <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/10/20 18:49:50 by gcyril            #+#    #+#             */
/*   Updated: 2019/11/05 21:09:57 by gcyril           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memmove(void *dest, const void *src, size_t len)
{
	char		*destc;
	const char	*srcc;

	destc = (char *)dest;
	srcc = (const char *)src;
	if (!dest && dest == src)
		return (0);
	if (srcc <= destc)
	{
		while (len--)
			destc[len] = srcc[len];
	}
	else
		while (len--)
			*destc++ = *srcc++;
	return (dest);
}
